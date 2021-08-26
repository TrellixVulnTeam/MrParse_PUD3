"""
Created on 23 Jul 2021

@author: hlasimpk
"""
from collections import OrderedDict
import gemmi
import logging
import os
import numpy as np
import requests
from simbad.util.pdb_util import PdbStructure


class PdbModelException(Exception):
    pass


AF_BASE_URL = 'https://alphafold.ebi.ac.uk/entry/'
PDB_DIR = 'pdb_files'
MODELS_DIR = 'models'

logger = logging.getLogger(__name__)


class ModelData(object):
    OBJECT_ATTRIBUTES = ['hit', 'region']

    def __init__(self):
        self.avg_plddt = None
        self.sum_plddt = None
        self.date_made = None
        self.molecular_weight = None
        self.model_url = None
        self.pdb_file = None
        self.h_score = None
        self.rmsd = None
        self.hit = None
        self.region = None
        self.plddt_regions = None

    @property
    def length(self):
        return self._get_child_attr('hit', 'length')

    @property
    def name(self):
        fields = self._get_child_attr('hit', 'name').split("-")
        return fields[1] + fields[2][2:]

    @property
    def model_id(self):
        return self._get_child_attr('hit', 'name').split("-")[1]

    @property
    def range(self):
        return (self.query_start, self.query_stop)

    @property
    def region_id(self):
        return self._get_child_attr('hit', 'region_id')

    @property
    def region_index(self):
        return self._get_child_attr('hit', 'region_index')

    @property
    def score(self):
        return self._get_child_attr('hit', 'score')

    @property
    def seq_ident(self):
        seq_id = self._get_child_attr('hit', 'local_sequence_identity')
        if seq_id:
            return seq_id / 100.0
        return None

    @property
    def query_start(self):
        return self._get_child_attr('hit', 'query_start')

    @property
    def query_stop(self):
        return self._get_child_attr('hit', 'query_stop')

    # miscellaneous properties
    @property
    def static_dict(self):
        """Return a self representation with all properties resolved, suitable for JSON"""
        d = {k: self.__dict__[k] for k in self.__dict__.keys() if k not in self.OBJECT_ATTRIBUTES}
        # Get all properties
        for name in dir(self.__class__):
            obj = getattr(self.__class__, name)
            if name != 'static_dict' and isinstance(obj, property):
                val = obj.__get__(self, self.__class__)
                d[name] = val
        # Need to add in properties as these aren't included
        # FIX ONCE UPDATED JS TO HANDLE TWO INTS
        d['range'] = "{}-{}".format(*self.range)
        return d

    def _get_child_attr(self, child, attr):
        if hasattr(self, child):
            child = getattr(self, child)
            if hasattr(child, attr):
                return getattr(child, attr)
        return None

    def __str__(self):
        attrs = [k for k in self.__dict__.keys() if not k.startswith('_')]
        line_template = "  {} : {}\n"
        out_str = "Class: {}\nData:\n".format(self.__class__)
        for a in sorted(attrs):
            out_str += line_template.format(a, self.__dict__[a])
        return out_str


def models_from_hits(hits, pdb_dir=None):
    pdb_dir = pdb_dir or PDB_DIR
    if not os.path.isdir(pdb_dir):
        os.mkdir(pdb_dir)
    if not os.path.isdir(MODELS_DIR):
        os.mkdir(MODELS_DIR)
    models = OrderedDict()
    for hit in hits.values():
        mlog = ModelData()
        mlog.hit = hit
        hit._homolog = mlog
        mlog.model_url = AF_BASE_URL + hit.pdb_id.split('-')[1]
        try:
            mlog.pdb_file, mlog.molecular_weight, \
            mlog.avg_plddt, mlog.sum_plddt, mlog.h_score, mlog.date_made, mlog.plddt_regions = prepare_pdb(hit, pdb_dir)
        except PdbModelException as e:
            logger.critical("Error processing hit pdb %s", e.message)
        models[mlog.name] = mlog
    return models


def download_model(pdb_name):
    """Download AlphaFold2 model"""
    url = 'https://alphafold.ebi.ac.uk/files/' + pdb_name
    query = requests.get(url)
    return query.text


def prepare_pdb(hit, pdb_dir):
    """
    Download pdb or take file from cache
    trucate to required residues
    calculate the MW
    """
    pdb_name = "{}-model_v1.pdb".format(hit.pdb_id.split(":")[1])
    pdb_struct = PdbStructure()
    try:
        pdb_string = download_model(pdb_name)
        pdb_struct.structure = gemmi.read_pdb_string(pdb_string)

        # Remove first model
        models = [m.name for m in pdb_struct.structure]
        del pdb_struct.structure[models[0]]

        date_made = pdb_string.split('\n')[0].split()[-1]
    except RuntimeError:
        # SIMBAD currently raises an empty RuntimeError for download problems.
        raise PdbModelException("Error downloading PDB file for: {}".format(hit.pdb_id))
    pdb_file = os.path.join(pdb_dir, pdb_name)
    pdb_struct.save(pdb_file)

    seqid_range = range(hit.hit_start, hit.hit_stop + 1)
    pdb_struct.select_residues(to_keep_idx=seqid_range)

    avg_plddt = calculate_avg_plddt(pdb_struct.structure)
    sum_plddt = calculate_sum_plddt(pdb_struct.structure)
    h_score = calculate_quality_h_score(pdb_struct.structure)
    plddt_regions = get_plddt_regions(pdb_struct.structure, hit.seq_ali)

    # Convert plddt to bfactor score
    pdb_struct.structure = convert_plddt_to_bfactor(pdb_struct.structure)

    truncated_pdb_name = "{}_{}_{}-{}.pdb".format(hit.pdb_id, hit.chain_id, hit.hit_start, hit.hit_stop)
    truncated_pdb_path = os.path.join(MODELS_DIR, truncated_pdb_name)
    pdb_struct.save(truncated_pdb_path,
                    remarks=["PHASER ENSEMBLE MODEL 1 ID {}".format(hit.local_sequence_identity)])
    return truncated_pdb_path, int(pdb_struct.molecular_weight), avg_plddt, sum_plddt, h_score, date_made, plddt_regions


def calculate_quality_threshold(struct, plddt_threshold=70):
    res = above_threshold = 0
    for chain in struct[0]:
        for residue in chain:
            res += 1
            if residue[0].b_iso >= plddt_threshold:
                above_threshold += 1
    return (100.0 / res) * above_threshold


def calculate_quality_h_score(struct):
    score = 0
    for i in reversed(range(1, 101)):
        if calculate_quality_threshold(struct, plddt_threshold=i) >= i:
            score = i
            break
    return score


def get_plddt(struct):
    plddt_values = []
    for chain in struct[0]:
        for residue in chain:
            plddt_values.append(residue[0].b_iso)
    return plddt_values


def get_plddt_regions(struct, seqid_range):
    regions = {}
    plddt_values = get_plddt(struct)
    residues = zip(seqid_range, plddt_values)

    v_low = []
    low = []
    confident = []
    v_high = []

    for i, plddt in residues:
        if plddt < 50:
            v_low.append(i)
        elif 70 > plddt > 50:
            low.append(i)
        elif 90 > plddt > 70:
            confident.append(i)
        elif plddt > 90:
            v_high.append(i)

    regions['v_low'] = _get_regions(v_low)
    regions['low'] = _get_regions(low)
    regions['confident'] = _get_regions(confident)
    regions['v_high'] = _get_regions(v_high)

    return regions


def _get_regions(residues):
    regions = []
    start = finish = None
    for i in residues:
        if start:
            if i - 1 == finish:
                finish = i
            else:
                regions.append([start, finish])
                start = i
                finish = i
        else:
            start = i
            finish = i
    if start:
        regions.append([start, finish])
    return regions


def calculate_avg_plddt(struct):
    plddt_values = get_plddt(struct)
    return sum(plddt_values) / len(plddt_values)


def calculate_sum_plddt(struct):
    plddt_values = get_plddt(struct)
    return sum(plddt_values)


def convert_plddt_to_bfactor(struct):
    for chain in struct[0]:
        for residue in chain:
            for atom in residue:
                plddt_value = atom.b_iso
                atom.b_iso = _convert_plddt_to_bfactor(plddt_value)
    return struct


def _convert_plddt_to_bfactor(plddt):
    lddt = plddt / 100
    if lddt <= 0.5:
        return 657.97  # Same as the b-factor value with an rmsd estimate of 5.0
    rmsd_est = (0.6 / (lddt ** 3))
    bfactor = ((8 * (np.pi ** 2)) / 3.0) * (rmsd_est ** 2)
    if bfactor > 999.99:
        return 999.99
    return bfactor
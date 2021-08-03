"""
Created on 18 Oct 2018

@author: jmht
"""
import logging
from mrparse import mr_homolog 
from mrparse import mr_alphafold
from mrparse import mr_hit
from mrparse.mr_region import RegionFinder
from mrparse import mr_pfam
from mrparse.mr_util import now

logger = logging.getLogger(__name__)


class SearchModelFinder(object):
    def __init__(self, seq_info, hkl_info=None, pdb_dir=None, db_lvl=None):
        self.seq_info = seq_info
        self.hkl_info = hkl_info
        self.pdb_dir = pdb_dir
        self.db_lvl = db_lvl
        self.hits = None
        self.model_hits = None
        self.regions = None
        self.model_regions = None
        self.homologs = None
        self.models = None

    def __call__(self):
        """Required so that we can use multiprocessing pool. We need to be able to pickle the object passed
        to the pool and instance methods don't work, so we add the object to the pool and define __call__
        https://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-multiprocessing-pool-map/6975654#6975654
        """
        logger.debug('SearchModelFinder started at %s' % now())
        try:
            self.find_homolog_regions()
            logger.debug('SearchModelFinder homolog regions done at %s' % now())
            self.prepare_homologs()
            logger.debug('SearchModelFinder homologs done at %s' % now())
        except AssertionError:
            pass
        try:
            self.find_model_regions()
            logger.debug('SearchModelFinder model regions done at %s' % now())
            self.prepare_models()
            logger.debug('SearchModelFinder models done at %s' % now())
        except AssertionError:
            pass
        return self
    
    def find_homolog_regions(self):
        self.hits = mr_hit.find_hits(self.seq_info, dblvl=self.db_lvl)
        if not self.hits:
            logger.critical('SearchModelFinder PDB search could not find any hits!')
            return None
        self.regions = RegionFinder().find_regions_from_hits(self.hits)
        return self.regions

    def find_model_regions(self):
        self.model_hits = mr_hit.find_hits(self.seq_info, dblvl="af2")
        if not self.model_hits:
            logger.critical('SearchModelFinder EBI Alphafold database search could not find any hits!')
            return None
        self.model_regions = RegionFinder().find_regions_from_hits(self.model_hits)
        return self.model_regions

    def prepare_homologs(self):
        assert self.hits and self.regions
        self.homologs = mr_homolog.homologs_from_hits(self.hits, self.pdb_dir)
        if self.hkl_info:
            mr_homolog.calculate_ellg(self.homologs, self.hkl_info)
        return self.homologs

    def prepare_models(self):
        assert self.model_hits and self.model_regions
        self.models = mr_alphafold.models_from_hits(self.model_hits, self.pdb_dir)
        return self.models

    def homologs_as_dicts(self):
        """Return a list of per homlog dictionaries serializable to JSON"""
        if not (self.regions and len(self.regions)):
            raise RuntimeError("No regions generated by SearchModelFinder")
        return [h.static_dict for h in self.homologs.values()]

    def models_as_dicts(self):
        """Return a list of per model dictionaries serializable to JSON"""
        if not (self.model_regions and len(self.model_regions)):
            raise RuntimeError("No regions generated by SearchModelFinder")
        return sorted([m.static_dict for m in self.models.values()], key=lambda k: k['sum_plddt'], reverse=True)[:20]

    def homologs_with_graphics(self):
        """List of homologs including PFAM graphics directives
        
        This needs to be done better - the PFAM graphics shouldn't be stored in the 
        list of homologs - this was just done because it made development quicker.
        The list of homologs and PFAM graphics needs to be kept separate
        """
        if not (self.regions and len(self.regions)):
            raise RuntimeError("No regions generated by SearchModelFinder")
        mr_pfam.add_pfam_dict_to_homologs(self.homologs, self.seq_info.nresidues)
        return self.homologs_as_dicts()

    def models_with_graphics(self):
        """List of models including PFAM graphics directives

        This needs to be done better - the PFAM graphics shouldn't be stored in the
        list of models - this was just done because it made development quicker.
        The list of models and PFAM graphics needs to be kept separate
        """
        if not (self.model_regions and len(self.model_regions)):
            raise RuntimeError("No regions generated by SearchModelFinder")
        mr_pfam.add_pfam_dict_to_models(self.models, self.seq_info.nresidues)
        return self.models_as_dicts()

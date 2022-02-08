import argparse
import os
import sys

if sys.version_info.major < 3:
    import ConfigParser
else:
    import configparser as ConfigParser

from mrparse.mr_version import __version__


class FilePathAction(argparse.Action):
    """Class to handle paths to files or directories.
    
    We cd into a work directory so relative paths to files don't work.
    We set absolulte paths here.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str):
            values = os.path.abspath(values)
        setattr(namespace, self.dest, values)


def mrparse_argparse(parser):
    """Parse MrParse command line arguments"""
    # Read command line arguments
    sg = parser.add_argument_group("Basic options")
    sg.add_argument('-hkl', '--hklin', action=FilePathAction, help='MTZ/CIF Crystal Data file')
    sg.add_argument('--do_classify', action='store_true',
                    help='Run the SS/TM/CC classifiers - requires internet access.')
    sg.add_argument('--pdb_dir', action=FilePathAction, help='Directory of PDB files')
    sg.add_argument('--phmmer_dblvl', help='Redundancy level of PDB database used by Phmmer', default='95',
                    choices=['50', '70', '90', '95', '100'])
    sg.add_argument('--plddt_cutoff', help='Removes residues from AFDB models below this pLDDT threshold',
                    default='70', choices=['50', '70', '90', 'None'])
    sg.add_argument('--run_serial', action='store_true', help='Run on a single processor')
    sg.add_argument('-seq', '--seqin', action=FilePathAction, help='Sequence file')
    sg.add_argument('--search_engine', help="Select search engine", default="phmmer",
                    choices=['phmmer', 'hhsearch'])
    sg.add_argument('--tmhmm_exe', action=FilePathAction,
                    help="Location of TMHMM executable for transmembrane classification")
    sg.add_argument('--deepcoil_exe', action=FilePathAction,
                    help="Location of Deepcoil executable for coiled-coil classification")
    sg.add_argument('--hhsearch_exe', action=FilePathAction,
                    help="Location of hhsearch executable")
    sg.add_argument('--hhsearch_db', help="Location of hhsearch database")
    sg.add_argument('--ccp4cloud', action='store_true', help="specify running through CCP4Cloud")
    sg.add_argument('-v', '--version', action='version', version='%(prog)s version: ' + __version__)


def parse_command_line():
    """Parse MrParse command line arguments"""
    # Read config file, check for local config file for documentation
    if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "mrparse.config")):
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "mrparse.config")
    else:
        config_file = os.path.join(os.environ["CCP4"], "share", "mrparse", "data", "mrparse.config")
    defaults = {}
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    defaults.update(dict(config.items("Defaults")))
    defaults.update(dict(config.items("Executables")))
    defaults.update(dict(config.items("Databases")))

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    mrparse_argparse(parser)
    parser.set_defaults(**defaults)
    args = parser.parse_args()

    # Add executables and databases to config file so that it only needs to be specified once
    update_config = False
    if args.tmhmm_exe != defaults['tmhmm_exe']:
        config.set('Executables', 'tmhmm_exe', args.tmhmm_exe)
        update_config = True
    if args.deepcoil_exe != defaults['deepcoil_exe']:
        config.set('Executables', 'deepcoil_exe', args.deepcoil_exe)
        update_config = True
    if args.hhsearch_exe != defaults['hhsearch_exe']:
        config.set('Executables', 'hhsearch_exe', args.hhsearch_exe)
        update_config = True
    if args.hhsearch_db != defaults['hhsearch_db']:
        config.set('Databases', 'hhsearch_db', args.hhsearch_db)
        update_config = True
    if update_config:
        with open(config_file, 'w') as f:
            config.write(f)

    return args

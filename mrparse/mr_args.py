import argparse
import os


class FilePathAction(argparse.Action):
    """Class to handle paths to files or directories.
    
    We cd into a work directory so relative paths to files don't work.
    We set absolulte paths here.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str):
            values = os.path.abspath(values)
        setattr(namespace, self.dest, values)

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hklin', action=FilePathAction, help='MTZ/CIF Crystal Data file')
    parser.add_argument('--no_classify', action='store_true', help='Do not run the classifiers - avoids online access')
    parser.add_argument('--pdb_dir', action=FilePathAction, help='Directory of PDB files')
    parser.add_argument('--run_serial', action='store_true', help='Run on a single processor')
    parser.add_argument('--seqin', action=FilePathAction, required=True, help='Sequence file')
    return parser.parse_args()
 
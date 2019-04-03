#!/usr/bin/env ccp4-python
# encoding: utf-8
'''
mrparse.main -- shortdesc

mrparse.main is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2018 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

from argparse import ArgumentParser
import logging.config
import json
import os
import sys

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
logging_json = os.path.join(THIS_DIR, 'logging.json')
with open(logging_json, 'rt') as f:
    config = json.load(f)
logging.config.dictConfig(config)
logger = logging.getLogger()

# Set up logging before doing any more importing to make sure we log everything
MRPARSE_DIR = os.path.join(THIS_DIR, '..')
sys.path.insert(0, MRPARSE_DIR)
from mrparse import mr_analyse
#print("'%s'" % logger.handlers[0].formatter._fmt)

def main():
    '''Command line options.'''
    program_name = os.path.basename(sys.argv[0])
    logger.info("Starting: %s", program_name)
    try:
        # Setup argument parser
        parser = ArgumentParser()
        parser.add_argument('-hklin', help='MTZ/CIF Crystal Data file')
        parser.add_argument('-seqin', help='Sequence file')

        # Process arguments
        args = parser.parse_args()
        mr_analyse.run(args.seqin, hklin=args.hklin)

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        indent = len(program_name) * " "
        logger.error(program_name + ": " + repr(e) + "\n", exc_info=True)
        logger.error(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())
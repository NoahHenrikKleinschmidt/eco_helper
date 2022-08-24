"""
The top-level main command line interface.
"""

import argparse
import eco_helper.convert.cli as convert
import eco_helper.format.cli as format
import eco_helper.normalise.cli as normalise
import eco_helper.enrich.cli as enrich

def setup_parser():

    descr = """
                  __         __                 
  ___  ___ ___    | |__   ___| |_ __   ___ _ __ 
 / _ \/ __/ _ \   | '_ \ / _ \ | '_ \ / _ \ '__|
|  __/ (_| (_) |  | | | |  __/ | |_) |  __/ |   
 \___|\___\___/___|_| |_|\___|_| .__/ \___|_|   
            |_____|           |_|              

A command-line toolbox for data pre-processing streamlined to work with the EcoTyper framework.
    """
    parser = argparse.ArgumentParser( description=descr, formatter_class=argparse.RawDescriptionHelpFormatter )
    command = parser.add_subparsers( dest = "command" )
    convert.setup_parser( command )
    format.setup_parser( command )
    normalise.setup_parser( command )
    enrich.setup_parser( command )
    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()
    args.func( args )


if __name__ == '__main__':
    main()
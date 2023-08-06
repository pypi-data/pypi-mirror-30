"""A command parser for UNIX Shell"""
import argparse
import os
import yaml
from astrosql import apass, astrosql, writer
from astrosql.procedure import update, calibration

dir = os.path.dirname(__file__)
config_file = os.path.join(dir, '../config.yml')
with open(config_file, 'r') as ymlfile:
    config = yaml.safe_load(ymlfile)

APASS_HEADER = config['apass']['headers']

def parse_args(args):
    """Parse linux command arguments and calls on the proper astroSQL commands:"""
    global parent_parser
    global parser

    ## Global Commands ##
    # Global/Parent Parser: All commands here are inherited by those with parents=[parent_parser] argument
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v", "--verbose", help="verbose", action="store_true")
    parent_parser.add_argument(
        "--time", help="records time", action="store_true")

    # Main Parser: Parses the main command `astrosql` and parents to subparsers (handling subcommands)
    parser = argparse.ArgumentParser(
        prog="astroSQL", description=astrosql.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[parent_parser])
    parser.set_defaults(func=None)

    # Subparsers: Parses subcommands
    subparsers = parser.add_subparsers()
    parse_import(subparsers)
    parse_calibration(subparsers)
    parse_apass(subparsers)
    parse_update(subparsers)
    return parser.parse_args(args)

def parse_apass(subparsers):
    """Parser for APASS Query"""
    parser_apass = subparsers.add_parser("apass", aliases=[
                                         "APASS"], description=writer.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[parent_parser])
    # Enable Web Retrieval
    parser_apass.add_argument("ra", type=float)
    parser_apass.add_argument("dec", type=float)
    parser_apass.add_argument("radius", type=float)
    parser_apass.add_argument(
        "-o", "--outfile", help="save query result to an ouput file")
    parser_apass.add_argument(
        '-w', '--web', action='store_true', help="retrieve data from APASS website \"https://www.aavso.org/apass\" (Default: False)")
    parser_apass.add_argument(
        '-d', '--database', action='store_true', help="by default, retrieve data from MySQL database (Default: True)", default='True')
    parser_apass.add_argument(
        "-u", "--user", help="MySQL username (default: user entered later)")
    parser_apass.add_argument(
        "-p", "--password", help="MySQL password (default: password entered later)")
    parser_apass.add_argument(
        '-l', '--limit', help="Number of rows of data to retreive (Default: all)")
    #TODO: parser_apass.add_argument("--format", default="csv", help="Format output as csv or html. Enabled if [-w] enabled (Default: csv)")
    parser_apass.set_defaults(func=apass.main)

def parse_calibration(subparsers):
    """Parser for Aperture Calibration"""
    print("parse_calibration here")
    parser_calibration = subparsers.add_parser('calibration', aliases=[
                                               'calibrate'], description=calibration.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[parent_parser])
    parser_calibration.add_argument(
        "image", help="image fits file")
    parser_calibration.add_argument(
        "--passband", choices=['B', 'V', 'R', 'I', 'clear'], help="the passband of the image (default: tries to guess from image filename otherwise defaults to 'clear')")
    parser_calibration.add_argument(
        "-o", "--outfile", help="save calibrated data to an ouput file")

    # Mutually exclusive group where only one of these argument may be passed
    group = parser_calibration.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "reference", nargs='?', default=None, help="reference text-based file to be calibrated. May use '--from' instead (optional, default: None)")
    group.add_argument(
        "--from", dest='query', help="get data from a database like (e.g., '--in apass 5 5 1') (default: None)")

    parser_calibration.set_defaults(func=calibration.main)

def parse_import(subparsers):
    """Parser for Importing Data"""
    parser_import = subparsers.add_parser(
        'import', aliases=["import_data"], description=writer.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[parent_parser])
    parser_import.add_argument(
        "infile", help="absolute or relative path to file")
    parser_import.add_argument(
        "table", help="MySQL table to create or append")
    parser_import.add_argument("-d", "--database", help="MySQL database to write (default: config.yml or else errors)")
    parser_import.add_argument(
        "-u", "--user", help="MySQL username (default: config.yml or be prompted later)")
    parser_import.add_argument(
        "-p", "--password", help="MySQL password (default: config.yml password prompted later)")
    parser_import.add_argument(
        "--host", default='localhost', help="hostname where MySQL is hosted (default: 'localhost')")
    parser_import.add_argument(
        "-c", "--column_header", nargs='+',
        default=APASS_HEADER,
        help="Specify column header names for the table as a list of python strings [\"col1\", \"col2\", ...]. Please use config.yml before attempting this (default: config.yml)")
   
    parser_import.set_defaults(func=writer.main)

def parse_update(subparsers):
    """Parser for updating the database"""
    parser_update = subparsers.add_parser(
        'update', description=update.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[parent_parser])
    parser_update.add_argument('image', help="image fits file formatted as either relative or full path")
    parser_update.add_argument('-s', '--skip', action='store_true', help="skip WCS (default: False)")
    parser_update.add_argument('-d', '--delete', action='store_true', help="delete original image")
    parser_update.add_argument('-f', '-u', '--update', '--force', action='store_true', help="force an update regardless if new data is calibrated")

    parser_update.set_defaults(func=update.main)

def run(args):
    if args.func == writer.main:
        print("Importing data")
        results = writer.main(args)
    elif args.func == apass.main:
        if args.web:
            print("Query APASS from AAVSO online database")
        else:
            print("Query APASS from local database")
        #TODO: args.format = 1 if args.format == "csv" else 0
        result = apass.main(args)
    elif args.func == calibration.main:
        print("Calibrating aperature data")
        if args.query:
            args.reference = run(parse_args(args.query))
        result = calibration.main(args)
    elif args.func == update.main:
        results = update.main(args)
    else:
        print("Running Default")
        results = astrosql.main(args)
    return results

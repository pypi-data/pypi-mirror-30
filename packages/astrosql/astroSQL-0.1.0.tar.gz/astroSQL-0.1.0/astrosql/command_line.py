#!/usr/bin/env python
"""
Database tools for astronomers. 
The following subcommands are supported and called by "astroSQL [subcommand]":
    
    astroSQL      Not implemented
    import_data   Imports text - based file to MySQL server(ALIAS: data_to_mysql)
    APASS         Queries the APASS local or online database (ALIAS: apass)
"""
import os
import sys
import timeit
from pathlib import Path

root_path = Path(os.path.dirname(os.path.realpath(__file__)))
src_path = root_path/"src"
sys.path.append(str(root_path))
sys.path.append(str(src_path))

from astrosql import argparser


def main(args):
    print("astrosql.main not implemented")


if __name__ == "__main__":
    args = argparser.parse_args(sys.argv[1:])
    if args.verbose: print(args)
    if args.time: start = timeit.default_timer()
    result = argparser.run(args)
    if args.verbose: print(result)
    if args.time:
        stop = timeit.default_timer()
        time = (stop - start)
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        print("{:d}h {:02d}m {:02f}s".format(int(h), int(m), s))

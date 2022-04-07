import argparse
import logging
import tempfile
from datetime import datetime
from pathlib import Path


def parse_cli_args(namespace):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=Path, required=True,
                        help="Input file")
    parser.add_argument("--output", "-o", type=Path,
                        help="Output file",
                        default=Path(tempfile.gettempdir()) / Path(f"{datetime.today().strftime('%Y%m%d')}.csv"))
    parser.add_argument("-v", action="count", help="verbosity flag (v, vv, vvv, vvvv")
    args = parser.parse_args(namespace)
    if args.v:
        args.v = 50 - (args.v * 10)
        args.v = logging.DEBUG if args.v < 10 else args.v
    else:
        args.v = logging.INFO

    return args

"""
Parsing Alpha Progression Workout Output
"""
import sys
from collections import defaultdict, namedtuple
import logging
from pathlib import Path
from datetime import datetime
import re

from alpha_parse import cli, parse, session
import pandas as pd
from parse import parse_input_csv

if __name__ == "__main__":
    args = cli.parse_cli_args(sys.argv[1:])

    logging.basicConfig(level=args.v)
    df_csv = parse.parse_input_csv(args.input)

    logging.info(f"Writing parsed data to {args.output}")
    df_csv.to_csv(args.output, index=False)

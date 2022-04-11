"""
Parsing Alpha Progression Workout Output
"""
import sys
import logging

from alpha_parse import cli, parse


if __name__ == "__main__":
    args = cli.parse_cli_args(sys.argv[1:])

    logging.basicConfig(level=args.v)
    df_csv = parse.parse_input_csv(args.input)

    logging.info(f"Writing parsed data to {args.output}")
    df_csv.to_csv(args.output, index=False)

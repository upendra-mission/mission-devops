#!/usr/bin/env python3
import argparse
import sys
import os
import shutil
import tempfile

def deduplicate_lines(input_path, outfile, verbose=False):
    seen = set()
    total_lines = 0
    unique_lines = 0
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            total_lines += 1
            if line not in seen:
                outfile.write(line)
                seen.add(line)
                unique_lines += 1
    if verbose:
        print(f"Input lines: {total_lines}", file=sys.stderr)
        print(f"Unique output lines: {unique_lines}", file=sys.stderr)

def usage():
    usage_text = f"""
usage: {sys.argv[0]} INPUT_FILE [--output OUTPUT_FILE | --inplace] [--verbose | -v]

Remove duplicate lines from a CSV file, preserving order.

Positional arguments:
  INPUT_FILE           Path to input CSV file

Optional arguments:
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Path to write output CSV (does not modify input)
  --inplace            Rewrite the input file in place (uses temp file)
  -v, --verbose        Print input and output line counts to stderr
  -h, --help           Show this help message and exit

If neither --output nor --inplace are specified, output is written to stdout.
"""
    print(usage_text, file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        usage()
        sys.exit(0 if '-h' in sys.argv or '--help' in sys.argv else 1)

    parser = argparse.ArgumentParser(
        description='Remove duplicate lines from a CSV file, preserving order.',
        add_help=False,
        usage=argparse.SUPPRESS
    )

    parser.add_argument('input_file', nargs='?', help='Path to input CSV file')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o', '--output', dest='output_file', help='Path to write output CSV (does not modify input)')
    group.add_argument('--inplace', action='store_true', help='Rewrite the input file in place (uses temp file)')

    parser.add_argument('-v', '--verbose', action='store_true', help='Print input and output line counts to stderr')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')

    args = parser.parse_args()

    if args.help or not args.input_file:
        usage()
        sys.exit(0 if args.help else 1)

    if args.inplace:
        dir_name = os.path.dirname(os.path.abspath(args.input_file))
        with tempfile.NamedTemporaryFile(delete=False, encoding='utf-8', dir=dir_name) as tmpfile:
            deduplicate_lines(args.input_file, tmpfile, verbose=args.verbose)
            tmpname = tmpfile.name
        try:
            shutil.copyfile(tmpname, args.input_file)
            os.remove(tmpname)
        except Exception as e:
            print(f"Error while replacing file: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as output_file:
            deduplicate_lines(args.input_file, output_file, verbose=args.verbose)

    else:
        deduplicate_lines(args.input_file, sys.stdout, verbose=args.verbose)

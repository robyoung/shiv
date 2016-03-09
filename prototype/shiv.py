import sys
import csv
import argparse
import re


class Range(object):
    @staticmethod
    def from_str(s):
        try:
            parts = s.split('-')
            lower, upper = None, None

            if len(parts) == 1:
                lower, upper = int(parts[0]), int(parts[0])
            elif len(parts) == 2:
                if len(parts[0]) == 0:
                    lower, upper = 1, int(parts[1])
                elif len(parts[1]) == 0:
                    lower, upper = int(parts[0]), sys.maxsize
                else:
                    lower, upper = int(parts[0]), int(parts[1])
            else:
                raise ValueError
        except ValueError:
            raise ValueError("Invalid range {}".format(s))

        return Range(lower, upper)

    def __init__(self, lower, upper):
        if lower > upper:
            raise ValueError("Lower must be lower than upper")
        if lower < 1:
            raise ValueError("Ranges start from 1")
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return r"<Range lower={} upper={}>".format(self.lower, self.upper)


def parse_delimiter(delimiter):
    return delimiter.replace(r'\t', "\t") if delimiter else delimiter


def parse_args(in_args):
    parser = argparse.ArgumentParser("shiv")
    parser.add_argument("-d", "--delimiter")
    parser.add_argument("-f", "--fields")
    parser.add_argument("-e", "--extract", type=re.compile)
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--tsv", action="store_true")
    parser.add_argument("-o", "--out-delimiter")
    parser.add_argument("files", nargs='*')

    args = parser.parse_args(in_args)

    args.fields = [
        Range.from_str(field_range)
        for field_range in args.fields.split(',')
    ]

    args.delimiter = parse_delimiter(args.delimiter)

    if not args.out_delimiter:
        if args.delimiter:
            args.out_delimiter = args.delimiter
        elif args.csv:
            args.out_delimiter = ","
        else:
            args.out_delimiter = "\t"
    args.out_delimiter = parse_delimiter(args.out_delimiter)

    action_count = sum(map(bool,
                           [args.delimiter, args.extract, args.csv, args.tsv]))
    if action_count == 0:
        args.delimiter = "\t"
    assert action_count < 2, \
        "You must have only one of --delimiter, --extract, --csv or --tsv"

    return args


def get_instream(file_paths, delimiter, is_csv, is_tsv):
    if len(file_paths):
        instream = (
            line for file_path in file_paths for line in open(file_path)
        )
    else:
        instream = sys.stdin
    if is_csv or is_tsv:
        instream = csv.reader(instream,
                              delimiter="," if is_csv else "\t",
                              quotechar='"')
    else:
        instream = (line.rstrip("\r\n") for line in instream)
        if args.delimiter:
            instream = (line.split(delimiter) for line in instream)
        elif args.extract:
            def ifmatch(line):
                match = extract.search(line)
                if match:
                    return match.groups()
            instream = (ifmatch(line) for line in instream)
    return instream


def get_outstream(out_delimiter, is_csv, is_tsv):
    if is_csv or is_tsv:
        writer = csv.writer(sys.stdout,
                            delimiter="," if is_csv else "\t",
                            quotechar='"')
        return lambda row: writer.writerow(row)
    else:
        def outstream(row):
            print(out_delimiter.join(row))
        return outstream


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    instream = get_instream(args.files, args.delimiter, args.csv, args.tsv)
    outstream = get_outstream(args.out_delimiter, args.csv, args.tsv)

    for in_fields in instream:
        out_fields = []
        if args.fields:
            for r in args.fields:
                out_fields += in_fields[r.lower - 1:r.upper]
        else:
            out_fields = in_fields
        outstream(out_fields)

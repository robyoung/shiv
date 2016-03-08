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


class FieldList(object):
    @staticmethod
    def from_str(s):
        return FieldList([Range.from_str(rs) for rs in s.split(",")])

    def __init__(self, ranges):
        self.ranges = ranges

    def __repr__(self):
        return r"<FieldList ranges={}>".format(self.ranges)


def parse_delimiter(delimiter):
    return delimiter.replace(r'\t', "\t")


def parse_args(in_args):
    parser = argparse.ArgumentParser("shiv")
    parser.add_argument("-d", "--delimiter", type=parse_delimiter)
    parser.add_argument("-f", "--fields", type=FieldList.from_str)
    parser.add_argument("-e", "--extract", type=re.compile)
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--tsv", action="store_true")
    parser.add_argument("-o", "--out-delimiter", type=parse_delimiter)
    parser.add_argument("files", nargs='*')

    args = parser.parse_args(in_args)

    action_count = sum(map(bool, [args.delimiter, args.extract, args.csv, args.tsv]))
    assert action_count > 0, "You must have one of --delimiter, --extract, --csv or --tsv"
    assert action_count < 2, "You must have only one of --delimiter, --extract, --csv or --tsv"

    if not args.out_delimiter:
        if args.delimiter:
            args.out_delimiter = args.delimiter
        elif args.csv:
            args.out_delimiter = ","
        else:
            args.out_delimiter = "\t"

    return args


def get_instream(file_paths):
    if len(file_paths):
        def linebyline():
            for file_path in file_paths:
                with open(file_path) as handle:
                    for line in handle:
                        yield line
        return linebyline
    else:
        return sys.stdin


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    instream = get_instream(args.files)

    if args.csv or args.tsv:
        instream = csv.reader(instream, delimiter="," if args.csv else "\t", quotechar='"')

    for line in instream:
        out_fields = []
        if args.csv or args.tsv:
            if not args.fields:
                out_fields = line
            else:
                for r in args.fields.ranges:
                    out_fields += line[r.lower - 1:r.upper]
        else:
            line = line.rstrip("\r\n")
            if args.delimiter:
                fields = line.split(args.delimiter)
                if not args.fields:
                    out_fields = fields
                else:
                    for r in args.fields.ranges:
                        out_fields += fields[r.lower - 1:r.upper]
            elif args.extract:
                match = args.extract.search(line)
                if match:
                    out_fields = match.groups()

        print(args.out_delimiter.join(out_fields))

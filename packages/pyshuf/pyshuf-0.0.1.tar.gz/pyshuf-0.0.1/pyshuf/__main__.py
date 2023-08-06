#!/usr/bin/env python

""" Shuffle the order of an input stream """

from __future__ import print_function
import random
import argparse
import sys

def get_lines(infile):

    lines = []
    while (True):
        try:
            line = raw_input()
            lines.append(line)
        except:
            break
    return lines

def shuffle_lines(lines):

    # return random.shuffle(lines)
    return random.sample(lines, len(lines))

def random_line(lines):

    return random.choice(lines)

def exit_error(msg, code=0):

    print (str(msg), file=sys.stderr)
    exit(0)

def lo_hi(lo_hi_str):

    lo_str, hi_str = lo_hi_str.split("-")
    lo = int(lo_str)
    hi = int(hi_str)

    return (lo, hi)
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e","--echo",
                        action="store_true",
                        help="Treat each command-line operand as an input line")
    parser.add_argument("-i","--input-range",
                        metavar="lo-hi",
                        help="Act as if input came from a file containing the range of unsigned decimal integers lo...hi, one per line.")
    parser.add_argument("-n","--head-count",
                        metavar="count",
                        type=int,
                        help="Output at most count lines")
    parser.add_argument("--input-file", type=file)

    try:
        args, unk = parser.parse_known_args()
    except Exception as e:
        exit_error(e)

    if args.input_file:
        lines = args.input_file.readlines()
    elif args.input_range:
        lo, hi = lo_hi(args.input_range)
        lines = [str(x) for x in range(lo, hi)]
    elif args.echo:
        lines = unk
    else:
        lines = get_lines(sys.stdin)

    count = len(lines)
    if args.head_count:
        count = args.head_count

    for line in shuffle_lines(lines)[:count]:
        print (line.rstrip("\n"))

if __name__ == "__main__":
    main()
    

    

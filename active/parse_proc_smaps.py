#!/usr/bin/env python3
#
# Modified version of https://github.com/craig08/parse_smaps
#

import sys
import os
from pathlib import Path
from collections import defaultdict, OrderedDict


def print_header(mem_idx):
    """Print the header of the memory allocation"""
    print("=" * 120)

    print(
        "{:>8}  {:>8}  {:>8}  {:>8}  {:>10}  {:>10} {:>13}      library".format(
            *mem_idx.keys(),
        )
    )
    print("=" * 120)


def print_row(meminfo, name):
    print(
        "{:>10} kB  {:>10} kB  {:>9} kB  {:>9} kB  {:>7} kB  {:>7} kB {:>10} kB"
        " {:<}".format(*meminfo, name)
    )


def main():
    mem_type = ""
    mem_idx = OrderedDict(
        [
            ("Private_Clean", 0),
            ("Private_Dirty", 1),
            ("Shared_Clean", 2),
            ("Shared_Dirty", 3),
            ("Rss", 4),
            ("Pss", 5),
            ("Size", 6),
        ]
    )

    smaps_file = os.path.abspath(sys.argv[1])

    mapinfo = defaultdict(lambda: [0] * len(mem_idx))
    total = [0] * len(mem_idx)
    file = [0] * len(mem_idx)
    file_cache = [0] * len(mem_idx)
    lib = [0] * len(mem_idx)
    filesinfo = defaultdict(lambda: [0] * len(mem_idx))

    with open(smaps_file, "r") as smap:
        for line in smap:
            line_arr = line.split()
            if "-" in line_arr[0]:
                if len(line_arr) < 6:
                    filename = "[anonymous]"
                else:
                    filename = " ".join(line_arr[5:])
            else:
                line_arr[0] = line_arr[0].strip(":")

            if line_arr[0] in mem_idx:
                mapinfo[filename][mem_idx[line_arr[0]]] += int(line_arr[1])
                total[mem_idx[line_arr[0]]] += int(line_arr[1])

    print_header(mem_idx)

    for filename, mem in sorted(mapinfo.items(), key=lambda x: -sum(x[1])):
        p = Path(filename)
        if p.parts[0] != "/":
            # not a path
            print_row(mem, filename)
            continue
        if len(p.parts) <= 2:
            print_row(mem, filename)
            continue

        if len(p.parts) <= 4:
            # e.g. /usr/lib/libX11-xcb.so.1.0.0
            p = str(p.parent)
        else:
            # first tree dirs
            p = "/" + "/".join(p.parts[1:4])
        filesinfo[p] = [sum(x) for x in zip(filesinfo[p], mem)]

    for k, v in filesinfo.items():
        print_row(v, k)

    print("=" * 120)
    print_row(total, "total")


if __name__ == "__main__":
    main()

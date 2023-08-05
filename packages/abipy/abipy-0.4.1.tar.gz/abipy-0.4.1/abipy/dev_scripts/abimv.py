#!/usr/bin/env python
"""
I use this script when I need to rerun interactively a task while preserving
the output files of the previous run.
"""

import sys
import os

def main():
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) != 2:
        print("Usage: abimv.py BKP_DIRNAME")
        return 0

    src_dir = "."
    dest_dir = sys.argv[1]
    if os.path.exists(dest_dir):
        print("Cannot overwrite: ", dest_dir)
        return 1
    src_dir = os.path.abspath(src_dir)
    dest_dir = os.path.abspath(dest_dir)
    os.mkdir(dest_dir)

    files = ["autoaral.json",  "job.sh", "queue.qerr", "queue.qout",
             "run.abi", "run.abo", "run.err",  "run.files",  "run.log",  "__startlock__"]

    for f in files:
        s = os.path.join(src_dir, f)
        if not os.path.exists(s): continue
        os.move(s, os.path.join(dest_dir, f))

    return 0

if __name__ == "__main__":
    sys.exit(main())

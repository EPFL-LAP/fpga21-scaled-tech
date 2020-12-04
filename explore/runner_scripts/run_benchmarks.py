"""Runs benchmarks.

Parameters
----------
arc : str
    Architecture file or directory holding multiple architectures.
circs : str
    Space-separated list of circuits to be used for searching for channel composition.
    Asterisk will generate files for all circuits.
log_dir : str
    Directory in which to store the logs.
keep : Optional[bool], deafult = False
    Instructs the script to keep the VPR files.
timeout : Optional[int], default = None
    Number of seconds until timeout of a single run.
is_magic : Optional[bool], default = False
    Turns on the magic flags (turns off the final high-effort ones).
"""

import os
import argparse
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../..')

import setenv

from parallelize import Parallel
from conf import *

parser = argparse.ArgumentParser()
parser.add_argument("--arc")
parser.add_argument("--circs")
parser.add_argument("--log_dir")
parser.add_argument("--keep")
parser.add_argument("--timeout")
parser.add_argument("--is_magic")
args = parser.parse_args()

KEEP = 0
try:
    KEEP = int(args.keep)
except:
    pass

TIMEOUT = None
try:
    TIMEOUT = int(args.timeout)
except:
    pass

IS_MAGIC = 0
try:
    IS_MAGIC = int(args.is_magic)
except:
    pass

os.system("mkdir %s" % args.log_dir)

call = "python -u run_vpr.py --arc %s --circ %s --seed %d" + (" --log_dir %s" % args.log_dir)\
     + (" --keep %d" % KEEP) + ((" --timeout %d" % TIMEOUT) if TIMEOUT is not None else '')\
     + (" --is_magic %d"  % IS_MAGIC)
calls = set()

max_cpu = int(os.environ["VPR_CPU"])
sleep_interval = 1

for N in grid_sizes:
    for circ in (grid_sizes[N] if args.circs == '*' else args.circs.split()):
        width = grid_sizes[N][circ]
        if os.path.isdir(args.arc):
            grid_dir = args.arc
            for f in os.listdir(grid_dir):
                if not "N%d" % N in f:
                    continue
                if f.endswith(".xml") and int(f.rsplit('W', 1)[1].rsplit("_H", 1)[0]) == width:
                    for seed in seeds:
                        calls.add(call % (grid_dir + f, "benchmarks/%s.blif" % circ, seed))
        else:
            for seed in seeds:
                calls.add(call % (args.arc, "benchmarks/%s.blif" % circ, seed))

calls = list(calls)

runner = Parallel(max_cpu, sleep_interval)
runner.init_cmd_pool(calls)
runner.run()

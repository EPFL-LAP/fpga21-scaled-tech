"""Generates all files needed by the search for good channel compositions.

Parameters
----------
tech : float
    Technology node (16, 7, 5, 4, 3.0, 3.1).
    3.0 corresponds to F3a in the paper and 3.1 to F3b.
N : int
    Cluster size.
circs : str
    Space-separated list of circuits to be used for searching for channel composition.
    Asterisk will generate files for all circuits.
wire : Optional[List[int]], default = None
    Specifies channel compositions for which to generate the architectures.
res_dir : Optional[str], default = magic_N%d_T%s % (args.N, args.tech)
    Result directory.
pad_only : Optional[bool], default = False
    Specifies that only the padding log should be produced.
import padding : Optional[bool], default = False
    Specifies that padding should be imported from N8 magic.

Returns
-------
None
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
parser.add_argument("--tech")
parser.add_argument("--N")
parser.add_argument("--circs")
parser.add_argument("--wire")
parser.add_argument("--res_dir")
parser.add_argument("--pad_only")
parser.add_argument("--import_padding")
args = parser.parse_args()

PAD_ONLY = False
try:
    PAD_ONLY = int(args.pad_only)
except:
    pass

IMPORT_PADDING = False
try:
    IMPORT_PADDING = int(args.import_padding)
except:
    pass

N = int(args.N)

used_sizes = set()

if args.circs == '*':
    for circ in grid_sizes[N]:
        used_sizes.add(grid_sizes[N][circ])
else:
    for circ in args.circs.split():
        try:
            used_sizes.add(grid_sizes[N][circ])
        except:
            print("Nonexistant cluster size, circuit pair: (%d, %s)" % N, circ)
            raise ValueError

used_sizes = list(sorted(used_sizes))

chan_dir = os.path.abspath("all_channels/") + '/'
res_dir = "magic_N%d_T%s/" % (N, args.tech)
if args.res_dir is not None:
    res_dir = args.res_dir
os.system("mkdir " + res_dir)
res_dir = os.path.abspath(res_dir) + '/'
call = "time python -u arc_gen.py --K 6 --N %d --wire_file %s --grid_w %d --grid_h %d --density 0.5 --tech %s --arc_name %s --physical_square 1"\
     + (" --only_pad 1" if PAD_ONLY else '') + (" --import_padding \"../explore/runner_scripts/all_circs_magic_N8_T%s/magic_T%s_N8_W%d_W13_H13_padding.log\"" if IMPORT_PADDING else '')
wd = os.getcwd()

arc_name = "magic_T%s_N%d_W%d_W%d_H%d.xml"
os.chdir("../../generate_architecture/")

max_cpu = int(os.environ["VPR_CPU"])
max_spice = int(os.environ["HSPICE_CPU"])
sleep_interval = 3

if args.wire is not None:
    WIRE = []
    for wire in args.wire.split():
        WIRE.append(int(wire))
else:
    WIRE = None

calls = []
grid_h = grid_w = used_sizes[0]
for c in os.listdir(chan_dir):
    if c.rsplit('T', 1)[1].split('_', 1)[0] != args.tech:
        continue
    c_cnt = int(c.split('_')[1].rsplit('.', 1)[0])
    if WIRE is not None and not c_cnt in WIRE:
        continue
    print(c)
    arc_name_concrete = arc_name % (args.tech, N, c_cnt, grid_w, grid_h)
    if arc_name_concrete in os.listdir(res_dir):
        continue
    if IMPORT_PADDING:
        calls.append(call % (N, chan_dir + c, grid_w, grid_h, args.tech, arc_name_concrete, args.tech, args.tech, c_cnt))
    else:
        calls.append(call % (N, chan_dir + c, grid_w, grid_h, args.tech, arc_name_concrete))

runner = Parallel(min(max_spice, max_cpu), sleep_interval)
runner.init_cmd_pool(calls)
runner.run()

del runner

if not PAD_ONLY and len(used_sizes) > 1:
    calls = []
    for size in used_sizes[1:]:
        grid_w = size
        grid_h = size
        for c in os.listdir(chan_dir):
            if c.rsplit('T', 1)[1].split('_', 1)[0] != args.tech:
                continue
            c_cnt = int(c.split('_')[1].rsplit('.', 1)[0])
            if WIRE is not None and not c_cnt in WIRE:
                continue
            print(c)
            arc_name_concrete = arc_name % (args.tech, N, c_cnt, grid_w, grid_h)
            if arc_name_concrete in os.listdir(res_dir):
                continue
            if IMPORT_PADDING:
                calls.append(call % (N, chan_dir + c, grid_w, grid_h, args.tech, arc_name_concrete, args.tech, args.tech, c_cnt)\
                             + " --change_grid_dimensions %s" % (arc_name % (args.tech, N, c_cnt, used_sizes[0], used_sizes[0])))
            else:
                calls.append(call % (N, chan_dir + c, grid_w, grid_h, args.tech, arc_name_concrete)\
                             + " --change_grid_dimensions %s" % (arc_name % (args.tech, N, c_cnt, used_sizes[0], used_sizes[0])))

    runner = Parallel(max_cpu, sleep_interval)
    runner.init_cmd_pool(calls)
    runner.run()

for size in used_sizes:
    grid_w = size
    grid_h = size
    for c in os.listdir(chan_dir):
        if c.rsplit('T', 1)[1].split('_', 1)[0] != args.tech:
            continue
        c_cnt = int(c.split('_')[1].rsplit('.', 1)[0])
        if WIRE is not None and not c_cnt in WIRE:
            continue
        print(c)
        arc_name_concrete = arc_name % (args.tech, N, c_cnt, grid_w, grid_h)
        if arc_name_concrete in os.listdir(res_dir):
            continue
        rr_name = arc_name_concrete.rsplit('.', 1)[0] + "_rr.xml.lz4"
        log_name = arc_name_concrete.rsplit('.', 1)[0] + "_padding.log"
        os.system("mv %s %s" % (log_name, res_dir))
        if not PAD_ONLY:
            os.system("mv %s %s" % (arc_name_concrete, res_dir))
            os.system("mv %s %s" % (rr_name, res_dir))
    if PAD_ONLY:
         break
 
os.chdir(wd)

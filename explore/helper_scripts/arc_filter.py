"""Filters out the architectures that are more than a given threshold
percent larger, or has a given percentage larger total delay than
the minimum found in the given directory.

Parameters
----------
arc_dir : str
    Directory holding the architecture descriptions.
area_thr : int
    Percentage of area increase threshold.
delay_thr : Optional[int], default = None
    Percentage of delay increase threshold

Returns
-------
str
    Space-separated list of architectures that survive filtering.
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--arc_dir")
parser.add_argument("--area_thr")
parser.add_argument("--delay_thr")
args = parser.parse_args()

DELAY_THR = None
try:
    DELAY_THR = float(args.delay_thr)
except:
    pass

arc_name = lambda f : '_'.join(f.split('_')[:-3]) if f.endswith("_padding.log") else None

area_dict = {}
delay_dict = {}
for f in os.listdir(args.arc_dir):
    name = arc_name(f)
    if name is None or name in area_dict:
        continue
    
    with open("%s/%s" % (args.arc_dir, f), "r") as inf:
        lines = inf.readlines()
    for line in lines:
        if line.startswith("Active dimensions:"):
            wa = int(line.split()[-4])
            ha = int(line.split()[-2])
        elif line.startswith("Metal dimensions:"):
            wm = int(line.split()[-4])
            hm = int(line.split()[-2])
            break
    a = max(wa, wm) * max(ha, hm) / 1000000.0
    area_dict.update({name : a})

    if DELAY_THR is None:
        continue
    
    with open("%s/%s" % (args.arc_dir, f.replace("_padding.log", ".xml")), "r") as inf:
        txt = inf.read()

    td = 0
    for w in txt.split():
        if "e-" in w and ("max=" in w):
            #NOTE: This only gets the wire access and feedback delays. Connection block is largely independent of
            #channel composition and wire delays themselves cannot be taken directly, as the logical length of each
            #wire would need to be taken into account.
            td += float(w.split('"')[1])
    delay_dict.update({name : td})

min_area = min([area_dict[arc] for arc in area_dict])
pass_area = min_area * (1 + float(args.area_thr) / 100)

if DELAY_THR is not None:
    min_delay = min([delay_dict[arc] for arc in delay_dict])
    pass_delay = min_delay * (1 + float(args.delay_thr) / 100)

passed = []
for arc in area_dict:
    if area_dict[arc] <= pass_area and (DELAY_THR is None or delay_dict[arc] <= pass_delay):
        passed.append(arc.split('_')[-1][1:])

#print("Passed: %d/%d" % (len(passed), len(area_dict)))
print(' '.join(sorted(passed, key = lambda p : int(p))) + "\n\n")

#print "unique_areas", len(set([area_dict[a] for a in area_dict if a.split('_')[-1][1:] in passed]))

#for p in sorted(area_dict, key = lambda a : area_dict[a]):
#    print p, area_dict[p]

import os
import sys
sys.path.insert(0,'..')

from conf import *

#Cluster size on which to perform the magic formula search.
N = 8
K = 6

#Circuits to be ignored, for the interest of time:
ignore_circs = ["frisc", "spla", "ex1010", "s38417", "pdc", "s38584.1", "clma"]
circs = sorted([circ for circ in grid_sizes[N] if not circ in ignore_circs])
circs = ' '.join(circs)

print circs

techs = ["16", "7", "5", "4", "3.0", "3.1"]

#Template for the stored files. Change as needed.
dir_template = "all_circs_magic_N%d_T%s/"

no_V1 = {2 : "V4 0", 4 : "V2 0", 8 : "V1 0", 16 : "V1 0"}
no_H1 = {2 : "H1 0", 4 : "H1 0", 8 : "H1 0", 16 : "H1 0"}

channel_dir = "all_channels/"
ENUM_CHANNELS = True
if os.path.isdir(channel_dir):
    ENUM_CHANNELS = False

for T in techs:
    if ENUM_CHANNELS:
        os.system("python -u enum_channel_compositions.py --K % d --N %d --tech %s --dump_dir %s"\
                 % (K, N, T, channel_dir))

    arc_dir = dir_template % (N, T)
    #Generate the necessary architecture files:
    os.system("python -u generate_files_for_magic_formula.py --N %d --tech %s --circs \"%s\" --res_dir %s/"\
             % (N, T, circs, arc_dir))

    #Removes those architectures that have no H1 or V1 wire equivalents in the channel
    #compositions. Without taps and at least with the given switch pattern, these are almost
    #never routable. Also, both Agilex and 7-Series architectures have such short wires, for a reason.
    for f in os.listdir(arc_dir):
        if f.endswith("_padding.log"):
            with open(arc_dir + f, "r") as inf:
                lines = inf.readlines()
            found = False
            for line in lines:
                if no_V1[N] in line or no_H1[N] in line:
                    found = True
                    break
            if found:
                print f
                os.system("rm -rf %s/%s*" % (arc_dir, f.split("_padding.log")[0]))

    #Run VPR:
    log_dir = arc_dir[:-1] + "_logs/"
    os.system("python clean_failed.py --log_dir %s --watch 1 &" % log_dir)
    os.system("python -u run_benchmarks.py --timeout 180 --is_magic 1 --arc %s --circ \"%s\" --log_dir %s" % (arc_dir, circs, log_dir))

    #Sort the architectures:
    wd = os.getcwd() + '/'
    arc_dir = wd + arc_dir
    log_dir = wd + log_dir
    sort_file = "%sall_circs_N8_T%s.sort" % (wd, T)
    os.system("python ../processing_scripts/sort_magic.py --arc_dir %s --log_dir %s --out_file %s --N 8 --tech %s --sort_key delay\
              --ignore_circs \"~ %s\"" % (arc_dir, log_dir, sort_file, T, circs))



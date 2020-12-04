"""Runs VPR on the specified circuit and architecture.
Results are stored in a log file.

Parameters
----------
arc : str
    Architecture file name.
circ : str
    Circuit file name.
seed : int
    Placement seed.
keep : Optional[bool], default = False
    Keep the files produced by VPR.
log_dir : Optional[str], default = '.'
    Directory in which to store the log.
force : Optional[bool], default = False
    Force override of a log that already exists.
    Otherise no run will be performed in that case.
timeout : Optional[int], default = None
    Specifies a timeout for VPR in seconds.
is_magic : Optional[bool], default = False
    Turns on the magic flags (turns off the final high-effort ones).

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

parser = argparse.ArgumentParser()
parser.add_argument("--arc")
parser.add_argument("--circ")
parser.add_argument("--seed")
parser.add_argument("--keep")
parser.add_argument("--log_dir")
parser.add_argument("--force")
parser.add_argument("--timeout")
parser.add_argument("--is_magic")
args = parser.parse_args()

arc_file = os.path.abspath(args.arc)
rr_archive = arc_file.rsplit(".xml", 1)[0] + "_rr.xml.lz4"
circ_file = os.path.abspath(args.circ)
seed = int(args.seed)

resdir = "%s_%s_%d" % (os.path.basename(arc_file).rsplit(".xml", 1)[0],\
                       os.path.basename(circ_file).rsplit(".blif", 1)[0],\
                       seed)
log_dir = None
try:
    log_dir = args.log_dir + '/'
except:
    pass

log_filename = (log_dir if log_dir is not None else '') + resdir + ".log"
FORCE = False
try:
    FORCE = args.force
except:
    pass

if not FORCE and os.path.exists(log_filename):
    print("Log exists. Run with --force 1 to override it.")
    exit(0)

IS_MAGIC = False
try:
    IS_MAGIC = int(args.is_magic)
except:
    pass

wd = os.getcwd()
os.system("mkdir %s" % resdir)
os.chdir(resdir)

os.system("cp %s ./" % arc_file)
os.system("cp %s ./" % rr_archive)
os.system("cp %s ./" % circ_file)

arc_file = os.path.basename(arc_file)
rr_archive = os.path.basename(rr_archive)
circ_file = os.path.basename(circ_file)
rr_file = rr_archive.rsplit(".lz4", 1)[0]

os.system("lz4 -d %s %s" % (rr_archive, rr_file))
with open(rr_file, "r") as inf:
    lines = inf.readlines()
for line in lines:
    if "chan_width_max" in line:
        words = line.split()
        for w in words:
            if "chan_width_max" in w:
                chan_w = int(w.split('"')[1])

TIMEOUT = None
try:
    TIMEOUT = int(args.timeout)
except:
    pass

precall = [("timeout %d " % TIMEOUT) if TIMEOUT is not None else '']

#NOTE: Some increase in horizontal wire congestion was observed for the
#smaller cluster sizes with normal VPR's length-based base cost scaling,
#likely due to the logically scaled vertical wires appearing much longer
#than for N=8. Also, in some cases, mismatch between the placed and routed
#delay was somewhat larger for smaller clusters, due to the delays being
#sampled at the I/O periphery, which has different connectivity than the
#the rest of the chip. In principle, changing the --place_delay_model_reducer
#could help in mitigating that, but in the end, after little experimentation,
#it was concluded that the most roubst results come from the default settings.
#In case of need, this may be revisited.
#
#Finally, the routability predictor was found to produce false positives 
#even if the circuit was routable on a particular architecture with prediction
#switched off. Hence, the predictor was kept during the search for magic formulas,
#as this is a process that requires routing a lot of different architectures, many
#of which are pathological, but it was turned off in the final experiments.
#Comment and uncomment the switches as needed.
base_vpr_flags = ["--seed %d" % seed,\
                  "--route_chan_width %d" % chan_w,\
                  "--read_rr_graph %s" % rr_file,\
                  "--router_lookahead map",\
                  #"--place_delay_model_reducer arithmean",\
                  #"--base_cost_type delay_normalized_frequency",\
                 ]
final_vpr_flags = ["--routing_failure_predictor off",\
                   "--router_max_convergence_count 5",\
                   "--max_router_iterations 100",\
                  ]
vpr_flags = base_vpr_flags + (final_vpr_flags if not IS_MAGIC else [])

vpr_args = [arc_file, circ_file]

os.system(' '.join(precall + [os.environ["VPR"]] + vpr_args + vpr_flags))

with open("vpr_stdout.log", "r") as inf:
    lines = inf.readlines()
for line in lines:
    if line.startswith("Final critical path:"):
        td = float(line.split()[3])
        break

os.chdir(wd)
with open(log_filename, "w") as outf:
    try:
        outf.write(str(td))
    except:
        outf.write("failed")

KEEP = False
try:
    KEEP = int(args.keep)
except:
    pass

if not KEEP:
    os.system("rm -rf %s" % resdir)

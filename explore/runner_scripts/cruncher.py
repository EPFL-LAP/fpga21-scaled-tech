"""This is the main runner script used to produce the final raw results.
It goes through the sorted list of magic formulas and generates architectures
for all cluster sizes and runs VPR experiments on all of them and all circuits
from the benchmark list, until the required number of fully routable formulas
are found and the corresponding routed delays obtained.

Parameters
----------
tech : float
    Technology node (16, 7, 5, 4, 3.0, 3.1).
    3.0 corresponds to F3a in the paper and 3.1 to F3b.
num : int
    Number of successful magic formulas sought.
skip : Optional[int], default = 0
    Number of magic formulas from the top of the sorted list to skip.

Returns
-------
None

Notes
-----
Some filename templates may need to be changed, depending on how the previous code
was run.
"""

import os
import time
import argparse
import sys
sys.path.insert(0,'..')
from conf import *

parser = argparse.ArgumentParser()
parser.add_argument("--tech")
parser.add_argument("--num")
parser.add_argument("--skip")
args = parser.parse_args()


arc_dir_template = "all_grids_N%d_T%s/"
log_dir_template = arc_dir_template[:-1] + "_logs/"

spice_template = "python -u generate_files_for_magic_formula.py --tech % s --N %d --circs \"*\" --res_dir %s --wire %d --import_padding 1 > /dev/null"

vpr_template = "python -u run_benchmarks.py --arc %s --log_dir %s --circs \"*\" > /dev/null"

clean = "rm -rf "
for seed in seeds:
    clean += "*_%d " % seed

sort_log = "all_circs_N8_T%s.sort" % args.tech

wires = []
with open(sort_log, "r") as inf:
    lines = inf.readlines()

for line in lines[1:]:
    wires.append(int(line.split()[0].split('W')[1]))

SKIP = 0
try:
    SKIP = int(args.skip)
except:
    pass

wires = wires[SKIP:]

##########################################################################
def spawn_ret_pid(cmd):
    """Calls the command and returns the process's pid.
    
    Parameters
    ----------
    cmd : str
        The command to run.

    Returns
    -------
    int
        pid of the worker process

    Notes
    -----
    Taken from stackexchange (https://stackoverflow.com/questions/20218570/
    how-to-determine-pid-of-process-started-via-os-system)
    """

    print cmd

    cmd += " & echo $! > pid"

    os.system(cmd)
    pid_file = open("pid", "r")
    pid = int(pid_file.read())
    pid_file.close()

    print "pid ", pid
    os.system("rm pid")

    return pid
##########################################################################

##########################################################################
def watch_status(pid, log_dir, arc_dir, wire):
    """Watches the status of the run. If there is a failure in any routing,
    kills the run and returns False. If the >>pid<< runner completes without
    failure, returns True.

    Parameters
    ----------
    pid : int
        Identifier of the VPR running process.
    log_dir : str
        Directory to watch on.
    arc_dir : str
        Architecture directory.
    wire : int
        Wire number. Used to move the successfully completed directories.

    Returns
    -------
    bool
        True if completed without failures, False otherwise.
    """

    while True:
        try:
            os.kill(pid, 0)
        except OSError:
            os.system("mv %s %s_%d/" % (arc_dir, arc_dir[:-1], wire))
            os.system("mv %s %s_%d/" % (log_dir, log_dir[:-1], wire))
            return True
        
        os.system("grep -r fail %s | wc > failure_detect.dump" % log_dir)
        with open("failure_detect.dump", "r") as inf:
            txt = inf.read()
        os.system("rm -rf failure_detect.dump")
        if int(txt.split()[0]) != 0:
            os.system("ps aux |grep python |grep -v \'cruncher.py\' |awk \'{print $2}\' |xargs kill")
            os.system("pkill vpr")
            os.system(clean)
            os.system("rm -rf %s %s" % (arc_dir, log_dir))
            return False

        time.sleep(5)
##########################################################################


i = 0
succeeded = 0
while succeeded < int(args.num):
    wire = wires[i]
    i += 1
    for N in Ns:
        arc_dir = arc_dir_template % (N, args.tech)
        log_dir = log_dir_template % (N, args.tech)
        spice_call = spice_template % (args.tech, N, arc_dir, wire)
        vpr_call = vpr_template % (arc_dir, log_dir)
        os.system(spice_call)
        pid = spawn_ret_pid(vpr_call)
        not_failed = watch_status(pid, log_dir, arc_dir, wire)
        if not not_failed:
            break
    if not_failed:
        succeeded += 1
    print succeeded

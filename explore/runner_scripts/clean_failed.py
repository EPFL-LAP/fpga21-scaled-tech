"""Deletes the failed architectures from the specified directory.
Can be used for speeding up magic runs by removing jobs that make
no sense. 

FIXME: A more elegant and automated solution is due.

Parameters
----------
log_dir : str
    Log directory.
rm_logs : Optional[bool], default = False
    Remove the failed logs as well.
watch : Optional[bool], default = False
    Instructs the script to keep watching on the log directory.

Returns
-------
None
"""

import os
import time
import argparse
import copy

parser = argparse.ArgumentParser()
parser.add_argument("--log_dir")
parser.add_argument("--rm_logs")
parser.add_argument("--watch")
args = parser.parse_args()

log_dir = args.log_dir + '/'
arc_dir = log_dir.rsplit("_logs", 1)[0] + '/'

RM_LOGS = False
try:
    RM_LOGS = int(args.rm_logs)
except:
    pass

WATCH = False
try:
    WATCH = int(args.watch)
except:
    pass

while not os.path.isdir(log_dir):
    time.sleep(5)

false_alert = 0
old_failed = None
while True:
    failed = set()
    for f in os.listdir(log_dir):
        with open(log_dir + f, "r") as inf:
            txt = inf.read().strip()
    
        if "fail" in txt:
            base_name = '_'.join(f.split('_')[:-4]) + '_'
            failed.add(base_name)
    
    for name in failed:
        os.system("pkill %s" % name)
        os.system("rm -rf %s*" % name)
        os.system("rm -rf %s/%s*" % (arc_dir, name))
        if RM_LOGS:
            os.system("rm -rf %s/%s*" % (log_dir, name))
    if old_failed != failed:
        false_alert = 0
        old_failed = copy.deepcopy(failed)
    else:
        false_alert += 1
    if not WATCH or false_alert > 60:
        break
    time.sleep(30)

"""A small script that allows for easy manual browsing of magic results.

Parameters
----------
tech : float
    Technology node (16, 7, 5, 4, 3.0, 3.1).
    3.0 corresponds to F3a in the paper and 3.1 to F3b.

Returns
-------
None

Notes
-----
Use 'n' and 'N' to navigate and 'q' to quit.
Sorting results filename template may need to be changed, depending on how the files were stored.
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--tech")
args = parser.parse_args()

sort_log = "magic_T%s.sort" % args.tech

##########################################################################
def print_stats(arc_no, lines):
    """Prints the architecture statistics.

    Parameters
    ----------
    arc_no : int
        Position of the architecture in the sorted list.
    lines : List[str]
        Parsed sort log.
    
    Returns
    -------
    str
        Architecture statistics.
    """

    log_line = lines[arc_no + 1]
    arc = log_line.split()[0]
    print(log_line)

    with open("%s/%s_padding.log" % (arc.rsplit('_', 1)[0], arc), "r") as inf:
        print(inf.read())
##########################################################################

with open(sort_log, "r") as inf:
    lines = inf.readlines()

min_line = 0
max_line = len(lines) - 2

line = min_line

while True:
    print_stats(line, lines)
    c = raw_input()
    if c == 'q':
        break
    elif c == 'n':
        line += 1
        if line > max_line:
            line -= 1
            print("Last architecture reached.")
    elif c == 'N':
        line -= 1
        if line < min_line:
            line += 1
            print("First architecture reached.")

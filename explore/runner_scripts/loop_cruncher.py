"""Simply loops through all technologies, calling >>cruncher.py<<.
The name of the script is such that cruncher will not kill it.
"""

import os
import sys
sys.path.insert(0,'..')

from conf import tech_nodes

num = 3

for tech in tech_nodes:
    os.system("time python -u cruncher.py --tech %s --num %d" % (str(tech), num))

"""Sets the necessary environment variables, for calling HSPICE and VPR.
"""

import os

#HSPICE command
os.environ["HSPICE"] = "/edadk/bin/eda snps hspice64" 

#VPR command
os.environ["VPR"] = "/root/vtr-verilog-to-routing-8.0.0/vpr/vpr" 

#Maximum parallel number of HSPICE jobs (depends on both the number of cores and licenses)
os.environ["HSPICE_CPU"] = "20"

#Maximum number of parallel VPR and other non-SPICE jobs
os.environ["VPR_CPU"] = "47"

# fpga21-scaled-tech

This repository holds the source code used to produce the results of the paper entitled "Global is the New Local: FPGA Architecture at 5nm and Beyond".

## Prerequisites

In order to reproduce the main results, Synopsys HSPICE (version 2013.12 was used in the paper) and VTR 8.0 are needed.
The corresponding commands are specified in [setenv.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/setenv.py). The same file contains two variables specifying the number
of parallel threads to be used for SPICE simulations, and for the remaining experiments (mainly VPR).

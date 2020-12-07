# fpga21-scaled-tech

This repository holds the source code used to produce the results of the paper entitled "Global is the New Local: FPGA Architecture at 5nm and Beyond".

## Prerequisites

In order to reproduce the main results, Synopsys HSPICE (version 2013.12 was used in the paper) and VTR 8.0 are needed.
The corresponding commands are specified in [setenv.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/setenv.py). The same file contains two variables specifying the number
of parallel threads to be used for SPICE simulations, and for the remaining experiments (mainly VPR).

## Code Organization

The source code is structured as follows:  

### SPICE Models

Directory [spice_models](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/spice_models/) contains transistor models for the 16nm node (F16), taken from [PTM](http://ptm.asu.edu/), as well as instructions on how to update the appropriate [ASAP7](http://asap.asu.edu/asap/) models to obtain the models used in the paper for the scaled technologies (F7--F3). Before running the experiments, the template files in this directory should be updated according to the instructions.


### Wire and Via Parameters

Directory [rc_calculations](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/) contains the scripts modeling the per-micrometer-length resistance and capacitance of wires as well as resistance of vias. It also contains the scripts to generate the results and produce the tables appearing in the submitted version of the paper, that can be run without any arguments ([generate_table_2.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/generate_table_2.py), [generate_table_3.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/generate_table_3.py),
[generate_table_4.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/generate_table_4.py)).

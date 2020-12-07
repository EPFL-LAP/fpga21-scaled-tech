# fpga21-scaled-tech

This repository holds the source code used to produce the results of the paper entitled "Global is the New Local: FPGA Architecture at 5nm and Beyond".

## Prerequisites

In order to reproduce the main results, Synopsys HSPICE (version 2013.12 was used in the paper) and VTR 8.0 are needed.
The corresponding commands are specified in [setenv.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/setenv.py). The same file contains two variables specifying the number
of parallel threads to be used for SPICE simulations, and for the remaining experiments (mainly VPR).  

For running the Python scripts, Python 2.7 is required.

## Code Organization and Result Reproduction

The source code is structured as follows:  

### SPICE Models

Directory [spice_models](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/spice_models/) contains transistor models for the 16nm node (F16), taken from [PTM](http://ptm.asu.edu/), as well as instructions on how to update the appropriate [ASAP7](http://asap.asu.edu/asap/) models to obtain the models used in the paper for the scaled technologies (F7--F3). Before running the experiments, the template files in this directory should be updated according to the instructions.


### Wire and Via Parameters

Directory [rc_calculations](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/) contains the scripts modeling the per-micrometer-length resistance and capacitance of wires as well as resistance of vias. It also contains the scripts to generate the results and produce the tables appearing in the submitted version of the paper, that can be run without any arguments ([generate_table_2.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/generate_table_2.py), [generate_table_3.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/generate_table_3.py),
[generate_table_4.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/rc_calculations/generate_table_4.py)).  

The produced results should be included in [tech.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/tech.py) (Those produced at the time of writing the paper are already embedded in the file).

### Logic Delays

Scripts for delay scaling between technology nodes, fanout-of-4-inverter (FO4) delay simulation, and generating the appropriate tables as they appeared in the submitted version of the paper ([generate_table6.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/logic_delays/generate_table6.py) and [generate_table7.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/logic_delays/generate_table7.py) are contained in [logic_delays/](https://github.com/EPFL-LAP/fpga21-scaled-tech/tree/master/logic_delays).  

The obtained scaled LUT and FF delays should be included in [tech.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/tech.py) (Those produced at the time of writing the paper are already embedded in the file).

### Wire Delay Measurement

The script for generating the SPICE netlists and measuring the delay of feedback intracluster wires (from the output of one LUT to inputs of other LUTs in the same cluster) and the delay of distributing an intercluster signal from the global wires to the LUT inputs is contained in [wire_delays/local_wires.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/local_wires.py). It provides various options, like repeater insertion and layer planning, described in the docstrings of the file.  

The same directory also contains a script that models global wire delay in a simplified manner, so as to appropriately size the drivers and determine tha maximum logical lengths of wires in a given technology and with a given cluster size ([global_wires.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/global_wires.py)]).  

Besides the delay modeling scripts, the directory also contains the scripts to generate the required numbers and plot the figures representing feedback delays in various settings, as used in the paper. To generate the data, run [get_figure_data.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/get_figure_data.py), without any arguments, which will produce additional Python files, containing the data, tagged with appropriate labels for plotting.  

To plot the figures, run `python plot_graphs_11_13.py --data figure_#`, where `#` is the number of the previously produced Python file (no extension is required).

### Buffer Sizing

As stated in the previous section, buffer sizing is performed by the delay modeling scripts in [wire_delays/](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/). The sizes, as well as the measured feedback delays are later used for complete architecture generation, stored in [wire_delays/buf_cache/](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/buf_cache/). To store the sizes for local wire drivers, run [build_local_buf_cache.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/build_local_buf_cache/), without arguments. Sizes of global wire drivers will be stored upon running [generate_table8.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/generate_table8.py), which also generates the table containing the maximum logical wire lengths, as it appeared in the submitted version of the paper.  

The obtained maximum lengths should be included in [tech.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/edit/master/tech.py) (Those produced at the time of writing the paper are already embedded in the file).  

Please note that, in some cases, the determined buffer sizes may be well matched to the fully modeled loads. To allow appropriate output signal transitions, in these cases, the sizes were manually changed by a small amount. The changes are documented in [buf_cache/notes.txt](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/wire_delays/build_local_buf_cache/notes.txt) and the entire cache as it appeared when writing the paper is included in the repository.

### Architecture Generation

VPR architecture and routing-resource graph descriptions are generated by [generate_architecture/arc_gen.py](https://github.com/EPFL-LAP/fpga21-scaled-tech/blob/master/generate_architecture/arc_gen.py). The script also provides more accurate modeling of global wire delays, including the wires connecting the LUT outputs to the switch-block multiplexers, etc. Many options are provided, whether as command line arguments or global variables at the top of the source file.
For the most part, they should be documented in the code itself, but please note that not all of them are guaranteed to work properly, as some were introduced only for preliminary experimentation and dropped either as not promising, or due to lack of time. To reproduce the results of the paper, there should not be any need to change any of the settings, nor to directly run this script.

### Running the Main Experiments



"""Changes the delays in an architecture file and the rr-graph.

Parameters
----------
arc : str
    Architecture to be modified.

Returns
-------
None
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--arc")

args = parser.parse_args()

get_val = lambda line, key : line.split("%s=\"" % key, 1)[1].split('"', 1)[0]
##########################################################################
def parse_delays(filename):
    """Parses all delays from an architecture file.

    Parameters
    ----------
    filename : str
        Name of the architecture file to be parsed.

    Returns
    -------
    Dict[str, various]
        A dictionary of all delays, indexed by their name,
        and holding the lines in which they occur as well.
    """

    with open(filename, "r") as inf:
        lines = inf.readlines()

    delay_dict = {}
    for line in lines:
        if "Tdel" in line:
            name = get_val(line, "name")
            td = float(get_val(line, "Tdel"))
            delay_dict.update({name : {"td" : td, "line" : line}})
        elif "delay_constant" in line:
            if "out_port=\"clb.O\"" in line:
                name = "lut_access"
            elif "in_port=\"ble" in line and "out_port=\"ble" in line:
                name = "feedback"
            else:
                continue
            td = float(get_val(line, "max"))
            delay_dict.update({name : {"td" : td, "line" : line}})

    return delay_dict
##########################################################################

#NOTE: Define the replacement dictionary here.
replacement_delays = {"H1" : 1.58e-11, "H2" : 1.99375e-11, "H4" : 2.8275e-11,\
                      "V4" : 1.99625e-11, "V8" : 3.7875e-11, "cb" : 3.47307e-11,\
                      "feedback" : 3.629e-11, "lut_access" : 2.79e-11}
replacement_delays = {"lut_access" : 16.85e-12, "feedback" : 50e-12}

replacement_delays = {"H1" : 1.72625e-11, "H2" : 1.99e-11, "H4" : 2.84438e-11,\
        "V4_tap_0" : 1.4425e-11, "V4_tap_1" : 2.52083e-12, "V4_tap_2" : 1.93333e-12, "V4_tap_3" : 2.6875e-12,\
        "V8_tap_0" : 3.1575e-11, "V8_tap_1" : 3.75e-12, "V8_tap_2" : 2.6625e-12, "V8_tap_3" : 3.2e-12, "cb" : 1.68703e-11,\
                      "feedback" : 1.147e-11, "lut_access" : 1.75e-11}

replacement_delays = {"H1" : 1.74125e-11, "H2" : 1.99875e-11, "H4" : 2.875e-11,\
                      "V1_tap_0" : 1.7625e-11, "V2_tap_0" : 3.11875e-11, "cb" : 3.29902e-11,\
                      "feedback" : 3.629e-11, "lut_access" : 1.685e-11}

replacement_delays = {"V8_tap_0" : 45.85e-12, "V4_tap_0" : 23.85834e-12}
#replacement_delays = {"feedback" : 49e-12}

delay_dict = parse_delays(args.arc)

#NOTE: Comment if unused.
equivalent_feedback_delay = lambda delay_dict : delay_dict["cb"]["td"]\
                                              + delay_dict["V4_tap_0"]["td"]\
                                              + delay_dict["V4_tap_1"]["td"]\
                                              + delay_dict["V4_tap_2"]["td"]\
                                              + delay_dict["V4_tap_3"]["td"]\
                                              + delay_dict["lut_access"]["td"]

##########################################################################
def replace_delays(delay_dict, replacement_delays):
    """Replaces the delays with the minimum between the previous entries
    in the parsed dictionary and the new entry. Vertical wire delays
    are distributed over taps according to the original ratios.

    Parameters
    ----------
    delay_dict : Dict[str, various]
        Dictionary to be updated.
    replacement_delays : Dict[str, float]
        Dictionary holding the potential new values.

    Returns
    -------
    None
    """

    #------------------------------------------------------------------------#
    def get_tap_fraction(wire, delay_dict):
        """Returns the delay fraction contributed by the current vertical wire segment.

        Parameters
        ----------
        wire : str
            Wire that is being processed.
        delay_dict : Dict[str, various]
            The delay dictionary.
       
        Returns
        -------
        float
            Fraction of the total delay.
        float
            Total delay.
        """

        if not "_tap" in wire:
            return 1.0, delay_dict[wire]["td"]

        total = 0
        base_name = wire.split("_tap")[0]
        for w in delay_dict:
            if w.startswith(base_name):
                total += delay_dict[w]["td"]

        return delay_dict[wire]["td"] / total, total
    #------------------------------------------------------------------------#

    for w in delay_dict:
        if replacement_delays.get(w, None) is not None:
            delay_dict[w]["td"] = replacement_delays[w]

    #NOTE: This part will scale the delays of tapped vertical wires with separated taps
    # and only accept better delays. Uncomment if this is needed.
    #for w in delay_dict:
    #    frac, total = get_tap_fraction(w, delay_dict)
    #    base_name = w if not "_tap" in w else w.split("_tap")[0]
    #    print w, replacement_delays.get(w, float('inf'))
    #    print total
    #    if replacement_delays.get(base_name, float('inf')) < total:
    #        delay_dict[w]["td"] = frac * replacement_delays[base_name]
##########################################################################
   
replace_delays(delay_dict, replacement_delays) 
try:
    print equivalent_feedback_delay(delay_dict)
except:
    pass

##########################################################################
def write_arc(delay_dict):
    """Writes out the architecture with replaced delays.

    Parameters
    ----------
    delay_dict : Dict[str, various]
        The delay dictionary.
       
    Returns
    -------
    None
    """
    
    with open(args.arc, "r") as inf:
        lines = inf.readlines()

    txt = ""
    for line in lines:
        replaced = False
        for w in delay_dict:
            if delay_dict[w]["line"] == line:
                txt += line.replace(get_val(line, "Tdel" if "Tdel" in line else "max"), str(delay_dict[w]["td"]))
                replaced = True
                break
        if not replaced:
            txt += line

    with open("%s/DelayChanged%s" % ('/'.join(args.arc.split('/')[:-1]), args.arc.split('/')[-1]), "w") as outf:
        outf.write(txt)
##########################################################################

##########################################################################
def write_rr(delay_dict):
    """Writes out the rr-graph with replaced delays.

    Parameters
    ----------
    delay_dict : Dict[str, various]
        The delay dictionary.
       
    Returns
    -------
    None
    """
    
    rr_filename = args.arc.replace(".xml", "_rr.xml")
    os.system("lz4 -d %s.lz4 %s" % (rr_filename, rr_filename))

    with open(rr_filename, "r") as inf:
        lines = inf.readlines()

    txt = ""
    switch_id = None
    for line in lines:
        if "<switch " in line:
            switch_id = get_val(line, "name")
            txt += line
            continue
        if "Tdel" in line and switch_id in delay_dict:
            txt += line.replace(get_val(line, "Tdel"), str(delay_dict[switch_id]["td"]))
            switch_id = None
        else:
            txt += line

    out_rr_filename = "%s/DelayChanged%s" % ('/'.join(rr_filename.split('/')[:-1]), rr_filename.split('/')[-1])

    with open(out_rr_filename, "w") as outf:
        outf.write(txt)

    os.system("lz4 %s %s.lz4" % (out_rr_filename, out_rr_filename))
    os.system("rm -f %s %s" % (rr_filename, out_rr_filename))
##########################################################################

write_arc(delay_dict)
write_rr(delay_dict)

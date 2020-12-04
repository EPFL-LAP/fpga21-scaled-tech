"""Enumerates all channel compositions in which LEN>1 wires do not
cause the architecture to be metal bound. LEN-1 wires are not explicitly
enumerated as they are padded to the chosen composition later.

Parameters
----------
K : int
    LUT size.
N : int
    Cluster size.
tech : float
    Technology node (16, 7, 5, 4, 3.0, 3.1).
    3.0 corresponds to F3a in the paper and 3.1 to F3b.
dump_dir : str
    Directory in which to store the results.

Returns
-------
None
"""

import os
import math
import itertools
import argparse
import sys
sys.path.insert(0,'../../')

import setenv
import tech

parser = argparse.ArgumentParser()
parser.add_argument("--K")
parser.add_argument("--N")
parser.add_argument("--tech")
parser.add_argument("--dump_dir")
args = parser.parse_args()

K = int(args.K)
N = int(args.N)

try:
    tech_node = int(args.tech)
except:
    tech_node = float(args.tech)

node_index = tech.nodes.index(tech_node)
node_device_index = tech.node_names.index(int(tech_node))

GP = tech.GP[node_device_index]
FP = tech.FP[node_device_index]
MyP = tech.MyP[node_index]

prototype_mux = 16
mux_w = float(21 + int(math.ceil(prototype_mux ** 0.5)))
#Size of the assumed average multiplexer. This assumption is neccessary
#in order to predict when the active tile width increase due to the added
#multiplexers and the width consumed by the vertical wires will balance out.
crossbar_and_cb_cols = 3
#Assumed number of crossbar and connection-block multiplexer columns.

lut_w = 16 * 10
#Width of the LUT SRAM mask, in fin pitches.
Wb = lut_w + crossbar_and_cb_cols * mux_w
#Fixed width due to LUT and local multiplexers.

lut_h = 2 ** (K - 4) * 12.0
#LUT height in gate pitches.

max_V_span = tech.max_V_span[node_index][K][N]
max_H_span = 8 if tech_node not in (4, 3.0) else 4

V_spans = [2 ** i for i in range(1, int(math.log(max_V_span, 2)) + 1)]
H_spans = [2 ** i for i in range(1, int(math.log(max_H_span, 2)) + 1)]

##########################################################################
def get_max_count(name, local_Wb = Wb):
    """Returns the maximum number of wires of the given span per LUT.

    Parameters
    ----------
    name : str
        Wire identifier.
    local_Wb : Optional[int], default = Wb
        Current active width.

    Returns
    -------
    int
        Maximum number of occurences of the wire per LUT.
    """

    L = int(name[1:])
    
    if name[0] == 'H':
        return int(math.floor(lut_h * GP / (2.0 * L * MyP)))

    alpha = 2.0 ** (K - 4)
    #Number of multiplexers per LUT height (if surpassed, a new column must be appended).

    return int(math.floor(local_Wb * FP / float(2.0 * N * L * MyP - mux_w / alpha * FP)))
##########################################################################

##########################################################################
def enum_h_channels():
    """Enumerates the legal horizontal channels.

    Parameters
    ----------
    None

    Returns
    -------
    List[Dict[str, int]]
        All legal horizontal channel compositions.
    """

    #-------------------------------------------------------------------------#
    def check_feas(comb, wire_ids):
        """Checks whether the composition is feasible.

        Parameters
        ----------
        comb : List[int]
            Composition.
        wire_ids : List[str]
            Wire Ids.

        Returns
        -------
        bool
            True if feasible False otherwise.
        """

        tracks = 0
        for i, c in enumerate(comb):
            L = int(wire_ids[i][1:])
            tracks += 2 * L * c

        return tracks * MyP <= lut_h * GP
    #-------------------------------------------------------------------------#

    #-------------------------------------------------------------------------#
    def pad_H1(comb, wire_ids):
        """Pads H1 wires.

        Parameters
        ----------
        comb : List[int]
            Composition.
        wire_ids : List[str]
            Wire Ids.

        Returns
        -------
        int
            Number of H1 wires that can be padded.
        """

        tracks = 0
        for i, c in enumerate(comb):
            L = int(wire_ids[i][1:])
            tracks += 2 * L * c

        return int(math.floor((lut_h * GP - tracks * MyP) / (2.0 * MyP)))
    #-------------------------------------------------------------------------#

    max_counts = {}
    for h in H_spans:
        h_name = "H%d" % h
        max_counts.update({h_name : get_max_count(h_name)})

    all_counts = {}
    for h in max_counts:
        all_counts.update({h : [0] +  [2 ** i for i in range(0, int(math.log(max_counts[h], 2)) + 1)]})

    wire_ids = sorted(max_counts, key = lambda w : int(w[1:]))

    max_mux_width = float("inf")
    min_V_chan_width = 1
    min_lut_drivers = 1

    count_lists = []
    for h in wire_ids:
        count_lists.append(all_counts[h])

    feasible = []
    for comb in itertools.product(*count_lists):
        if check_feas(comb, wire_ids):
            mux_width = 2 * (sum(comb) + pad_H1(comb, wire_ids)) + min_V_chan_width + min_lut_drivers
            if mux_width <= max_mux_width:
                feasible.append(comb)

    compositions = []
    for feas in feasible:
        compositions.append({})
        for i, c in enumerate(feas):
            compositions[-1].update({wire_ids[i] : c})
        compositions[-1].update({"H1" : pad_H1(feas, wire_ids)})

    return compositions
##########################################################################

##########################################################################
def enum_v_channels(h_wires):
    """Enumerates the legal vertical channels.

    Parameters
    ----------
    h_wires : int
        The number of used horizontal wires

    Returns
    -------
    List[Dict[str, int]]
        All legal horizontal channel compositions.
    """

    alpha = 2 ** (K - 4)
    #Number of multiplexers per LUT height (if surpassed, a new column must be appended).

    Wb_local = Wb + 2 * float(h_wires) / alpha * mux_w
    #Current active tile width (no vertical wire muxes at the moment).

    #-------------------------------------------------------------------------#
    def check_feas(comb, wire_ids, Wb_local):
        """Checks whether the composition is feasible.

        Parameters
        ----------
        comb : List[int]
            Composition.
        wire_ids : List[str]
            Wire Ids.

        Returns
        -------
        bool
            True if feasible False otherwise.
        """

        tracks = 0
        for i, c in enumerate(comb):
            L = int(wire_ids[i][1:])
            tracks += 2 * N * L * c

        return tracks * MyP <= (Wb_local + float(sum(comb)) / alpha * mux_w) * FP
    #-------------------------------------------------------------------------#

    #-------------------------------------------------------------------------#
    def pad_V1(comb, wire_ids, Wb_local):
        """Pads V1 wires.

        Parameters
        ----------
        comb : List[int]
            Composition.
        wire_ids : List[str]
            Wire Ids.

        Returns
        -------
        int
            Number of V1 wires that can be padded.
        """

        tracks = 0
        for i, c in enumerate(comb):
            L = int(wire_ids[i][1:])
            tracks += 2 * L * N * c


        return int(math.floor(((Wb_local + float(sum(comb)) / alpha * mux_w) * FP - tracks * MyP)\
              / float(MyP - mux_w / alpha * FP)))
    #-------------------------------------------------------------------------#

    max_counts = {}
    for v in V_spans:
        v_name = "V%d" % v
        max_counts.update({v_name : get_max_count(v_name, Wb_local)})

    all_counts = {}
    for v in max_counts:
        all_counts.update({v : ([0] +  [2 ** i for i in range(0, int(math.log(max_counts[v], 2)) + 1)]\
                           if max_counts[v] > 0 else [])})

    wire_ids = sorted(max_counts, key = lambda w : int(w[1:]))

    max_mux_width = 36
    #NOTE: We assume here that the switch-block pattern is full. To make the assumption more
    #realistic, we make the multiplexers substantially wider than what is really tollerated
    #during actual channel composition.
    min_lut_drivers = 1

    count_lists = []
    for v in wire_ids:
        count_lists.append(all_counts[v])

    feasible = []
    for comb in itertools.product(*count_lists):
        if check_feas(comb, wire_ids, Wb_local):
            v_wires = sum(comb) + pad_V1(comb, wire_ids, Wb_local)
            mux_width = max((2 * h_wires + v_wires), 2 * v_wires + h_wires) + min_lut_drivers
            if mux_width <= max_mux_width:
                feasible.append(comb)

    compositions = []
    for feas in feasible:
        compositions.append({})
        for i, c in enumerate(feas):
            compositions[-1].update({wire_ids[i] : c})

    return compositions
##########################################################################

##########################################################################
def export_channel(channel):
    """Exports the channel composition in the format understood by rr_graph_gen

    Parameters
    ----------
    channel : Tuple[Dict[str, int]]
        Horizontal and vertical channel compositions.

    Returns
    -------
    str
        Textual description.
    """

    h_chan, v_chan = channel
    wire_ids = sorted(h_chan, key = lambda w : int(w[1:]))
    
    txt = ""
    for h in wire_ids:
        if h == "H1" or h_chan[h] == 0:
            continue
        txt += "H %d %d\n" % (int(h[1:]), h_chan[h])
 
    wire_ids = sorted(v_chan, key = lambda w : int(w[1:]))
    for v in wire_ids:
        if v == "V1" or v_chan[v] == 0:
            continue
        txt += "V %d %d\n" % (int(v[1:]), v_chan[v])

    return txt
##########################################################################
   
h_channels = enum_h_channels()

channels = []
for h_chan in h_channels:
    for v_chan in enum_v_channels(sum([h_chan[h] for h in h_chan])):
        channels.append((h_chan, v_chan))

os.system("mkdir %s" % args.dump_dir)
for i, c in enumerate(channels):
    with open("%s/K%dN%dT%s_%d.wire" % (args.dump_dir, K, N, args.tech, i), "w") as outf:
        outf.write(export_channel(c))

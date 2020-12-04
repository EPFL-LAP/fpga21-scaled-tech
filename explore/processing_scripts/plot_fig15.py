import matplotlib.pyplot as plt
import numpy as np 
from scipy.interpolate import interp1d


#NOTE: Paste here the result of calling >>collect.py<<, as >>res_dict<<.
#All results obtained at the time of preparing the camera-ready version of the paper are kept here,
#including results for all three placement seeds, generated to inspect the robustness of the observations.
#While there were some shifts, all general trends were maintained across different placement seeds.


#New median seed:
res_dict = {'5': {8: {'wires': {129: {'index': 3, 'td': 1.28191912913}, 83: {'index': 1, 'td': 1.27114435737}, 121: {'index': 4, 'td': 1.27958421336}}, 'avg': 1.2764808114074981}, 16: {'wires': {129: {'index': 3, 'td': 1.49233811055}, 83: {'index': 1, 'td': 1.52882789737}, 121: {'index': 4, 'td': 1.53873562872}}, 'avg': 1.5239548560549272}, 2: {'wires': {121: {'index': 4, 'td': 1.31404437619}, 83: {'index': 1, 'td': 1.31290238906}, 129: {'index': 3, 'td': 1.32101026361}}, 'avg': 1.3165134425086404}, 4: {'wires': {129: {'index': 3, 'td': 1.26932501639}, 83: {'index': 1, 'td': 1.27839673572}, 121: {'index': 4, 'td': 1.26090082536}}, 'avg': 1.2680159860597475}}, '3.0': {8: {'wires': {31: {'index': 3, 'td': 1.58346258456}, 15: {'index': 2, 'td': 1.58043095382}, 47: {'index': 1, 'td': 1.56343729772}}, 'avg': 1.5727387079224027}, 16: {'wires': {15: {'index': 2, 'td': 2.23269437979}, 47: {'index': 1, 'td': 2.27262658724}, 31: {'index': 3, 'td': 2.28216168753}}, 'avg': 2.2630667424786295}, 2: {'wires': {31: {'index': 3, 'td': 1.51380629268}, 15: {'index': 2, 'td': 1.51798403695}, 47: {'index': 1, 'td': 1.52338478551}}, 'avg': 1.5205476787595527}, 4: {'wires': {47: {'index': 1, 'td': 1.46721054155}, 31: {'index': 3, 'td': 1.46791463764}, 15: {'index': 2, 'td': 1.47334918774}}, 'avg': 1.4672173838975753}}, '7': {8: {'wires': {56: {'index': 3, 'td': 1.35971679081}, 54: {'index': 5, 'td': 1.37471045121}, 55: {'index': 4, 'td': 1.36235250049}}, 'avg': 1.3640169673522868}, 16: {'wires': {56: {'index': 3, 'td': 1.65914721424}, 54: {'index': 5, 'td': 1.68053149572}, 55: {'index': 4, 'td': 1.58114667451}}, 'avg': 1.650798384170455}, 2: {'wires': {56: {'index': 3, 'td': 1.36666036143}, 54: {'index': 5, 'td': 1.38353225596}, 55: {'index': 4, 'td': 1.44236749599}}, 'avg': 1.3903007516096006}, 4: {'wires': {56: {'index': 3, 'td': 1.33584602781}, 54: {'index': 5, 'td': 1.36528719183}, 55: {'index': 4, 'td': 1.37518593956}}, 'avg': 1.358065270126699}}, '16': {8: {'wires': {156: {'index': 4, 'td': 1.69834394767}, 150: {'index': 5, 'td': 1.71483654569}, 78: {'index': 2, 'td': 1.69930401687}}, 'avg': 1.706571856740901}, 16: {'wires': {156: {'index': 4, 'td': 1.88852363622}, 78: {'index': 2, 'td': 1.88516168591}, 150: {'index': 5, 'td': 1.83496049834}}, 'avg': 1.874261012636684}, 2: {'wires': {156: {'index': 4, 'td': 1.7141098552}, 78: {'index': 2, 'td': 1.73404192348}, 150: {'index': 5, 'td': 1.76578177604}}, 'avg': 1.7356493060431721}, 4: {'wires': {156: {'index': 4, 'td': 1.6890900693}, 150: {'index': 5, 'td': 1.73097338485}, 78: {'index': 2, 'td': 1.69986187389}}, 'avg': 1.7054737665520063}}, '3.1': {8: {'wires': {62: {'index': 14, 'td': 1.29292342565}, 54: {'index': 11, 'td': 1.29140427105}, 47: {'index': 7, 'td': 1.26082535904}}, 'avg': 1.284928397528795}, 16: {'wires': {54: {'index': 11, 'td': 1.77395748973}, 62: {'index': 14, 'td': 1.80028959319}, 47: {'index': 7, 'td': 1.7203857828}}, 'avg': 1.7665257008033266}, 2: {'wires': {54: {'index': 11, 'td': 1.22721687408}, 62: {'index': 14, 'td': 1.21471478247}, 47: {'index': 7, 'td': 1.18470278664}}, 'avg': 1.2124984629842235}, 4: {'wires': {54: {'index': 11, 'td': 1.22674289253}, 62: {'index': 14, 'td': 1.20762412619}, 47: {'index': 7, 'td': 1.18842973457}}, 'avg': 1.2066327676821087}}, '4': {8: {'wires': {15: {'index': 2, 'td': 1.52156936382}, 63: {'index': 3, 'td': 1.58932748463}, 47: {'index': 1, 'td': 1.51416064709}}, 'avg': 1.5328022529605578}, 16: {'wires': {15: {'index': 2, 'td': 2.03656368986}, 63: {'index': 3, 'td': 2.0919312901}, 47: {'index': 1, 'td': 2.00019329663}}, 'avg': 2.0368197672007504}, 2: {'wires': {63: {'index': 3, 'td': 1.54429692709}, 47: {'index': 1, 'td': 1.47048963807}, 15: {'index': 2, 'td': 1.51544732447}}, 'avg': 1.5034079995100436}, 4: {'wires': {63: {'index': 3, 'td': 1.52567462918}, 47: {'index': 1, 'td': 1.44254475496}, 15: {'index': 2, 'td': 1.4815020229}}, 'avg': 1.4802757999518097}}}


colors = plt.cm.get_cmap("Set1")
xs = [1.2, 2.2, 3.2, 4.2, 5.2, 6.2]
Ns = [2, 4, 8, 16]
markers = ["o", "s", "^", "p"]
techs = ["16", "7", "5", "4", "3.0", "3.1"]

def plot_N(N, tech, data, label, avg = False):
    x = xs[techs.index(tech)] + Ns.index(N) * 0.16
    if not avg:
        for wire in data["wires"]:
            y = data["wires"][wire]["td"]
            plt.scatter(x, y, marker = markers[Ns.index(N)], c = colors(Ns.index(N) / float(len(Ns))), label= ("N = %d" % N) if label else None)
            plt.text(x, y, str(data["wires"][wire]["index"]), color="black", fontsize=8)
            label = False
    else:
        plt.scatter(x, data["avg"], marker = markers[Ns.index(N)], c = colors(Ns.index(N) / float(len(Ns))), label = ("N = %d" % N) if label else None)

xticklabels = ["F16", "F7", "F5", "F4", "F3a", "F3b"]

for t, tech in enumerate(techs):
    tech_xs = np.array([xs[t] + Ns.index(N) * 0.16 for N in Ns])
    tech_ys = np.array([res_dict[tech][N]["avg"] for N in Ns])
    x_new = np.linspace(tech_xs.min(), tech_xs.max(),500)
    f = interp1d(tech_xs, tech_ys, kind='quadratic')
    y_smooth=f(x_new)
    plt.plot(x_new,y_smooth, c='gray', zorder = 0, lw = 1)

labeled = False
for tech in techs:
    for N in reversed(Ns):
        plot_N(N, tech, res_dict[tech][N], label = not labeled, avg = True)
    labeled = True

plt.xticks([x + 0.24 for x in xs], xticklabels)
plt.xlim(0.7, 7)
plt.xlabel("Technology node")
plt.ylabel("[ns]")
plt.ylim(1.1, 2.3)

plt.legend()
plt.savefig("fig_15_max_seed.pdf")

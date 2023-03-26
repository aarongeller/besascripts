#!/usr/bin/python

import os, sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# see http://wiki.besa.de/index.php?title=Moving_Dipole_Fit

if len(sys.argv) < 4:
    print("Usage: python make_movingdipole_script.py <start_ms> <spacing_ms> <patientnum> [fnamestem] [numdipoles]")
    quit()
    
start_offset_ms = int(sys.argv[1])
spacing_ms = int(sys.argv[2])
patient_num = sys.argv[3]

output_path = os.path.join("/Users/aaron/Documents/BESA/megdata", patient_num, "figs")
if not os.path.isdir(output_path):
    os.makedirs(output_path)

if len(sys.argv)>4:
    fname_stem = sys.argv[4]
else:
    fname_stem = "movingdipole"
fname = os.path.join(output_path, fname_stem + "_" + patient_num + ".bbat")

if len(sys.argv)>5:
    num_dipoles = int(sys.argv[5])
else:
    num_dipoles = 11

gradient = np.linspace(0,1,num_dipoles)
cmap = mpl.colormaps["jet"]
chosen_colors_mat = cmap(gradient)

# make a colorbar figure that shows the color -> time mapping
times = []
for i in range(num_dipoles):
    times.append(start_offset_ms + i*spacing_ms)
times_str = list(map(lambda x: str(x), times))
plt.imshow(np.vstack((gradient, gradient)), aspect=0.5, cmap=cmap)
plt.xticks(np.arange(0,num_dipoles), times_str)
plt.yticks([])
plt.xlabel("Time (ms)")

# convert chosen colors to BGR for BESA
# besa appears to use decimal BGR code, i.e. (2^16)*blue + (2^8)*green + red,
# where blue, green, red are integers between 0 and 255 
decimal_colors = []
for i in range(num_dipoles):
    red_dec = int(round(255*chosen_colors_mat[i,0]))
    green_dec = int(round(255*chosen_colors_mat[i,1]))
    blue_dec = int(round(255*chosen_colors_mat[i,2]))

    decimal_colors.append(blue_dec*(2**16) + green_dec*(2**8) + red_dec)
    
part1 = "MAINFilter(LC:4.00-6dB-f,HC:40.00-24dB-z,NF:off,BP:off)\nMAINMarkBlock(WholeSegment,-,1,SendToSA)\nSAsetDefaultSourceType(Dipole)\nSAchannelTypeForFit(GRA)\nSAFitConstraint(RVOn:1.00,ENOff:1.00,MDOn:1.00,IMOff:1.00)\nSAaddSource(Dipole,UnitSphere,0.000,0.000,0.000,0.000,0.000,1.000,-," + str(decimal_colors[0]) + ",FitEnable,FitDisableOtherSources,BR29.bsa,1.00,30.00,Noise_)\nSAsetOrActivateSource(1,Disable)\nSAHeadModel(0)\nSAsetOrActivateSource(1,Enable)\nSAsetCursor(" + str(start_offset_ms) + ",NoDrawMap)\nSAfit(Sources)\nSAsetOrActivateSource(Last,Off)\n"

of = open(fname, 'w')
of.write(part1)

for i in range(num_dipoles-1):
    colornum = decimal_colors[i+1]
    part2 = "SAaddSource(Dipole,UnitSphere,0.000,0.000,0.000,0.000,0.000,1.000,-," + str(colornum) + ",FitEnable,FitDisableOtherSources)\nSAsetCursor(" + str(times[i+1]) + ",NoDrawMap)\nSAfit(Sources)\nSAsetOrActivateSource(Last,Off)\n"
    of.write(part2)

part3 = "SAsetOrActivateSource(All,On)\nSAfitInterval(" + str(start_offset_ms) + "," + str(start_offset_ms + spacing_ms*(num_dipoles - 1)) + ",FitInterval)\nSAsetOrActivateSource(1,Enable)\nSAdisplayMRI(On,SmallWindow,MultipleHeads)\n"
of.write(part3)

of.close()
plt.savefig(os.path.join(output_path, fname_stem + "_" + patient_num + ".png"))

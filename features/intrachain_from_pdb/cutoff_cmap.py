import os
import sys

import numpy as np

#used to apply cut off to the contact maps in case of predicted contact maps this can be used

in_file = sys.argv[1]
cut_off = float(sys.argv[2].strip())
out_dir = sys.argv[3]

# cut_off = 0.5
if not os.path.isfile(in_file):
    print("FILE DOESNT EXISTS ")
    exit()

pred_arr = np.loadtxt(in_file)
name = os.path.basename(in_file).split(".")[0]

out_file = out_dir + name + "_intra.cmap"
pred_arr[pred_arr <= cut_off] = 0
pred_arr[pred_arr > cut_off] = 1
np.savetxt(out_file, pred_arr)
print( "outfile "+str(out_file))

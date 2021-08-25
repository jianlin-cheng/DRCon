import copy
import math
import os.path
import sys

import numpy as np


def write2file(file, contents):
    with open(file, "w") as f:
        f.writelines(contents)
    f.close()


def file_reader(_seq_file):
    file = open(_seq_file, "r")
    output_array = []
    if file.mode == 'r':
        output_array = file.read().splitlines()
        file.close()
    return output_array[1]


out_array = []
Type_array = ['B', 'C', 'E', 'G', 'H', 'I', 'S', 'T']
# input_dir = "/home/rajroy/3FN2B.ss8"
input_dir = sys.argv[1]
ss_8 = file_reader(input_dir)
output_dir =sys.argv[2]
# output_dir="/home/rajroy/"
name = os.path.basename(input_dir).split(".")[0]
for type in Type_array:
    temp_array = []
    val = copy.deepcopy(np.array(list(ss_8.strip())))
    # print(len(val))
    temp_array = np.where(val == type, 1, 0)
    out_array.append(temp_array)
    # print(temp_array)
out_str = "# Sequence Length (log)" + "\n"
out_str = out_str + str(math.log(len(out_array[0])))[0:6] + "\n"
out_str = out_str + "# SS_8" + "\n"
for values in out_array:
    temp_str = ""
    for type in values:
        temp_str = temp_str + str(type) + " "
    out_str = out_str + temp_str.strip() + "\n"

print(out_str)
write2file(output_dir+str(name)+".feat_ss8",out_str)
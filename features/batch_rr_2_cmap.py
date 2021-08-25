import glob
import os
import sys

import numpy as np


def file_reader(_input):
    content_arry = []
    f = open(_input, "r")
    if f.mode == 'r':
        content_arry = f.read().splitlines()
        f.close()
    return content_arry

def writecmaps(file,contents):
    with open (file,"w") as f:
        f.write(contents+"\n")

def rr2cmap(_rr):
    file_read =  file_reader(_rr)
    length ,rr_array =len(file_read[0]), file_read[1:]
    _cmap = np.zeros((length,length))
    for val in rr_array:
        values = val.split(" ")
        _cmap[int(values[0]) - 1][int(values[1]) - 1] = values[4]
        _cmap[int(values[1]) - 1][int(values[0]) - 1] = values[4]
    return _cmap

# _inp ="//home/rajroy/casp_deephomo/deephomo_casp_rr/"
# out_put_dir = "/home/rajroy/experiment/cmap/"
_inp = sys.argv[1]
out_put_dir = sys.argv[2]
# input_dir = os.path.join("/media/rajroy/fbc3794d-a380-4e0f-a00a-4db5aad57e75/hdd/DeepHomo/DeepHomo_testset/Altered_benchmark/intra_rr/" , '*.rr')
input_dir = os.path.join(_inp , '*.rr')
# out_put_dir = "/media/rajroy/fbc3794d-a380-4e0f-a00a-4db5aad57e75/hdd/DeepHomo/DeepHomo_testset/Altered_benchmark/intra_cmap/"

protein_list = glob.glob(input_dir)
# val = np.loadtxt("/home/rajroy/features/feat/cmap/6GSX.cmap")
# print(val)
for val in protein_list:
    print(val)
    values = rr2cmap(val)
    # print(values)
    final_file = out_put_dir+ (os.path.basename(val).split("_")[0])+".cmap"
    if not os.path.exists(final_file):
        out_str = ""
        for v in values:
            temp_str = ""
            for inner_val in v:
                temp_str = temp_str+str(float(inner_val))+" "
            print(temp_str)
            out_str=out_str+temp_str+"\n"
        writecmaps(file=final_file,contents=out_str)

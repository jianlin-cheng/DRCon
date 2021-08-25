import copy
import os
import sys


def file_reader(input_dir):
    # reads pdb
    _input_dir = copy.deepcopy(input_dir)
    contents = ""
    f = open(_input_dir, "r")
    if f.mode == 'r':
        contents = f.read().splitlines()
        f.close()
    out_arr = []
    for val in contents:
        out_arr.append(val.strip())
    return out_arr


# Made for LEWIS SERVER -  SLURM SYSTEM
def specific_filename_reader(_input_dir, _extension):
    file_names = []
    for root, directories, files in os.walk(_input_dir):
        for file in files:
            if _extension in file:
                file_names.append(file.split(".")[0])
    return file_names


if len(sys.argv) != 5:
    print("Wrong input parameters\n\n")
    exit()

scratch_dir = sys.argv[1]
fasta_dir = sys.argv[2]
output_dir = sys.argv[3]
list_file = sys.argv[4]
list_of_list=  file_reader(list_file)
out_files = output_dir + "out/"
if not os.path.exists(output_dir):
    os.system("mkdir -p " + output_dir)
if not os.path.exists(out_files):
    os.system("mkdir -p " + out_files)

fasta_dir_files = specific_filename_reader(fasta_dir, ".fasta")
for values in fasta_dir_files:
    if values.strip() in list_of_list:
        if not os.path.exists(output_dir + values + ".ss"):
            os.chdir(out_files)
            cmd = "sh " + scratch_dir + " " + fasta_dir + values + ".fasta " + output_dir + values + " 4 \n"
            print(cmd)
            os.system(cmd)

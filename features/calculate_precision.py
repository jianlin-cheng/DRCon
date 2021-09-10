import copy
import os
import sys
import numpy as np
from utils.evalutaion.relaxed_cmaps import make_relax


# # NOTE
## This basically takes 2 contact maps as input and uses them to find the precision
## converts the real one into relax map of 0,1,2
##compares the top values

def file_reader(_input):
    content_arry = []
    f = open(_input, "r")
    if f.mode == 'r':
        content_arry = f.read().splitlines()
        f.close()
    return content_arry


def getY(true_file):
    input_array = []
    file = open(true_file, "r")
    if file.mode == 'r':
        input_array = file.read().splitlines()
        file.close()
    inter_array = []

    for values in input_array:
        inter_array.append(values.strip().split(' '))
    L = len(inter_array)
    relax_0_array = np.asfarray(inter_array, float)
    return relax_0_array


def loadFastaDictionary(dict_file):
    fasta_dict = {}
    with open(dict_file, "r") as f:
        for line in f:
            fasta_dict[line.strip().split(":")[0].strip()] = line.strip().split(":")[1].strip()
    return fasta_dict


def calculateEvaluationStats(_pred_cmap, _true_cmap, L, _name):
    pred_cmap = copy.deepcopy(_pred_cmap)
    true_cmap = copy.deepcopy(_true_cmap)
    prec_T5, prec_T10, prec_T20, prec_T30, prec_T50, prec_L30, prec_L20, prec_L10, prec_L5, prec_L, prec_2L, con_num = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    max_Top = int((2 * L) + 0.5)
    if 50 > max_Top: max_Top = 50

    for i in range(1, max_Top + 1):
        (x, y) = np.unravel_index(np.argmax(pred_cmap, axis=None), pred_cmap.shape)
        pred_cmap[x][y] = 0
        if true_cmap[x][y] == 1:
            con_num += 1
        if i == 5:
            prec_T5 = con_num * 20
            if prec_T5 > 100: prec_T5 = 100
            print("L=", L, "Val=", 5, "Con_num=", con_num)
        if i == 10:
            prec_T10 = con_num * 10
            if prec_T10 > 100: prec_T10 = 100
            print("L=", L, "Val=", 10, "Con_num=", con_num)
        if i == 20:
            prec_T20 = con_num * 5
            if prec_T20 > 100: prec_T20 = 100
            print("L=", L, "Val=", 20, "Con_num=", con_num)
        if i == 30:
            prec_T30 = con_num * 100 / 30
            if prec_T30 > 100: prec_T30 = 100
            print("L=", L, "Val=", 30, "Con_num=", con_num)
        if i == 50:
            prec_T50 = con_num * 2
            if prec_T50 > 100: prec_T50 = 100
            print("L=", L, "Val=", 50, "Con_num=", con_num)
        if i == int((L / 30) + 0.5):
            prec_L30 = con_num * 100 / i
            if prec_L30 > 100: prec_L30 = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)
        if i == int((L / 20) + 0.5):
            prec_L20 = con_num * 100 / i
            if prec_L20 > 100: prec_L20 = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)
        if i == int((L / 10) + 0.5):
            prec_L10 = con_num * 100 / i
            if prec_L10 > 100: prec_L10 = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)
        if i == int((L / 5) + 0.5):
            prec_L5 = con_num * 100 / i
            if prec_L5 > 100: prec_L5 = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)
        if i == int((L / 2) + 0.5):
            prec_L2 = con_num * 100 / i
            if prec_L2 > 100: prec_L2 = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)
        if i == int((L) + 0.5):
            prec_L = con_num * 100 / i
            if prec_L > 100: prec_L = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)
        if i == int((2 * L) + 0.5):
            prec_2L = con_num * 100 / i
            if prec_2L > 100: prec_2L = 100
            print("L=", L, "Val=", i, "Con_num=", con_num)

    return [prec_T5, prec_T10, prec_T20, prec_T30, prec_T50, prec_L30, prec_L20, prec_L10, prec_L5, prec_L2, prec_L,
            prec_2L,
            _name]


def get_evaluation_result(_arr, _relax, _SAMPLE_SIZE):
    sum_prec_T5, sum_prec_T10, sum_prec_T20, sum_prec_T30, sum_prec_T50, sum_prec_L30, sum_prec_L20, sum_prec_L10, sum_prec_L5, sum_prec_L2, sum_prec_L, sum_prec_2L = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    some_array = []
    for values in _arr:
        sum_prec_T5 = sum_prec_T5 + values[0]
        sum_prec_T10 = sum_prec_T10 + values[1]
        sum_prec_T20 = sum_prec_T20 + values[2]
        sum_prec_T30 = sum_prec_T30 + values[3]
        sum_prec_T50 = sum_prec_T50 + values[4]
        sum_prec_L30 = sum_prec_L30 + values[5]
        sum_prec_L20 = sum_prec_L20 + values[6]
        sum_prec_L10 = sum_prec_L10 + values[7]
        sum_prec_L5 = sum_prec_L5 + values[8]
        sum_prec_L2 = sum_prec_L2 + values[9]
        sum_prec_L = sum_prec_L + values[10]
        sum_prec_2L = sum_prec_2L + values[11]
        some_array.append(
            [values[12], str(values[0])[0:5], str(values[1])[0:5], str(values[2])[0:5], str(values[3])[0:5],
             str(values[4])[0:5],
             str(values[5])[0:5], str(values[6])[0:5], str(values[7])[0:5], str(values[8])[0:5], str(values[9])[0:5],
             str(values[10])[0:5], str(values[11])[0:5]])
    print(str(_relax) + '\t\t\t' + str(sum_prec_T5 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(sum_prec_T10 / _SAMPLE_SIZE)[
                                                                                     0:5] + '\t\t\t' + str(
        sum_prec_T20 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(sum_prec_T30 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(
        sum_prec_T50 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(sum_prec_L30 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(
        sum_prec_L20 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(sum_prec_L10 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(
        sum_prec_L5 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + '\t\t\t' + str(
        sum_prec_L2 / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(sum_prec_L / _SAMPLE_SIZE)[0:5] + '\t\t\t' + str(
        sum_prec_2L / _SAMPLE_SIZE)[0:5])

    return some_array


relax_0 = []
relax_1 = []
relax_2 = []
SAMPLE_SIZE = 0

real_cmap = sys.argv[1]
predict_cmap = sys.argv[2]

if os.path.isfile(real_cmap) and os.path.isfile(predict_cmap):
    SAMPLE_SIZE = SAMPLE_SIZE + 1
else:
    print("file not found")
    exit()

pred_arr = np.loadtxt(predict_cmap)
empty_cmap = np.zeros(pred_arr.shape)
name = os.path.basename(predict_cmap).replace('.txt', '')
real_arr = np.loadtxt(real_cmap)
relax_0.append(
    calculateEvaluationStats(pred_arr, real_arr, real_arr.shape[0], os.path.basename(real_cmap).split(".")[0]))
#
real_arr_1 = make_relax(real_arr, 1)
relax_1.append(
    calculateEvaluationStats(pred_arr, real_arr_1, real_arr.shape[0], os.path.basename(real_cmap).split(".")[0]))
#
real_arr_2 = make_relax(real_arr, 2)
relax_2.append(
    calculateEvaluationStats(pred_arr, real_arr_2, real_arr.shape[0], os.path.basename(real_cmap).split(".")[0]))

print(
    'RELAX ' + '\t\t\t' + 'TOP-5' + '\t\t\t' + 'TOP-10' + '\t\t\t' + 'TOP-20' + '\t\t\t' + 'TOP-30' + '\t\t\t' + 'TOP-50' + '\t\t\t' + 'L/30' + '\t\t\t' + 'L/20' + '\t\t\t' + 'L/10' +
    '\t\t\t' + 'L/5' + '\t\t\t' + '\t\t\t' + 'L/2' + '\t\t\t' + 'L/' + '\t\t\t' + '2L/')

relax_data_0 = get_evaluation_result(relax_0, 0, SAMPLE_SIZE)
relax_data_1 = get_evaluation_result(relax_1, 1, SAMPLE_SIZE)
relax_data_2 = get_evaluation_result(relax_2, 2, SAMPLE_SIZE)
print(SAMPLE_SIZE)

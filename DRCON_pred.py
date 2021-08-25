import copy
import time

import torch
# (49 + 1 +16 +526)
import torch.utils.data as data
import torch.nn as nn
import math
from torch.nn.utils.rnn import pad_sequence
import glob
from sklearn.metrics import precision_score, accuracy_score, recall_score, precision_recall_curve
from PIL import Image
import torchvision.transforms as transforms
from torch.utils.data import Dataset, TensorDataset
import torch.nn.functional as F
import copy
import csv
import os
import numpy as np
import math
import sys

# READ ALL THESE FROM A FILE
import resnet_model
import torch.optim as optim

model_path = sys.argv[1]
output_path = os.path.abspath(sys.argv[2])
NAMEOFFILE = sys.argv[3]
# DNCON FEATURE
feature_path = sys.argv[4]
# INTRA CHAIN PATH
intra_path = sys.argv[5]
# SS PATH
ss_path = sys.argv[6]
# TR_PATH
tr_path = sys.argv[7]

cmap_dir = output_path + "/cmap_" + NAMEOFFILE + ".cmap"

print(cmap_dir)
MAX_LENGTH = 600
EPOCH = 100
FEATURES = 592
RESNET_DEPTH = 36
# err_list = ['3QS2', '2HCK', '3NYO', '3NX3']
REJECT_LIST = ["# AA composition",
               "# intra",
               "# PSSM",
               "# NNCON",
               "# betacon",
               "# cov",
               "# plm",
               "# pre",
               "# pref score",
               "# Secondary Structure",
               "# Prediction at 60A",
               "# Prediction at 75A",
               "# Prediction at 80A",
               "# Prediction at 85A",
               "# Prediction at 10A",
               "# intra"

               ]

BATCH_SIZE = 1


def load_ss_features_only(_feature_file):
    L = 0
    with open(_feature_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            L = line.strip().split()
            L = int(round(math.exp(float(L[0]))))
            break
    Data = []
    with open(_feature_file, "r") as f:
        accept_flag = 1
        for line in f:
            if line.startswith('#'):
                if line.strip() == "SS_8":
                    accept_flag = 1
                else:
                    accept_flag = 1
                continue
            if accept_flag == 0:
                continue
            if line.startswith('#'):
                continue
            this_line = line.strip().split()
            if len(this_line) == 0:
                continue
            if len(this_line) == 1:
                feature2D = np.zeros((L, L))
                feature2D[:, :] = float(this_line[0])
                Data.append(feature2D)
            elif len(this_line) == L:
                feature2D1 = np.zeros((L, L))
                feature2D2 = np.zeros((L, L))
                for i in range(0, L):
                    feature2D1[i, :] = float(this_line[i])
                    feature2D2[:, i] = float(this_line[i])
                Data.append(feature2D1)
                Data.append(feature2D2)
            elif len(this_line) == L * L:
                feature2D = np.asarray(this_line).reshape(L, L)
                Data.append(feature2D)
            else:
                # print(line)
                print('Error!! Unknown length of feature in !!' + _feature_file)
                print('Expected length 0, ' + str(L) + ', or ' + str(L * L) + ' - Found ' + str(len(this_line)))
                sys.exit()
    Data = Data[1:17]
    F = len(Data)
    X = np.zeros((L, L, F))
    for i in range(0, F):
        X[0:L, 0:L, i] = Data[i]
    if np.isnan(np.sum(X)):
        os.system("echo '" + _feature_file + "' >> naninX.txt")
    return X


def load_features_dncon(_feature_file):
    reject_list = REJECT_LIST
    L = 0
    with open(_feature_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            L = line.strip().split()
            L = int(round(math.exp(float(L[0]))))
            break
    Data = []
    with open(_feature_file, "r") as f:
        accept_flag = 1
        for line in f:
            if line.startswith('#'):
                if line.strip() in reject_list:
                    accept_flag = 0
                else:
                    accept_flag = 1
                    # print(line)
                continue
            if accept_flag == 0:
                continue
            if line.startswith('#'):
                # print(line)
                continue
            this_line = line.strip().split()
            if len(this_line) == 0:
                continue
            if len(this_line) == 1:
                feature2D = np.zeros((L, L))
                feature2D[:, :] = float(this_line[0])
                Data.append(feature2D)
            elif len(this_line) == L:
                # 1D feature
                feature2D1 = np.zeros((L, L))
                feature2D2 = np.zeros((L, L))
                for i in range(0, L):
                    feature2D1[i, :] = float(this_line[i])
                    feature2D2[:, i] = float(this_line[i])
                Data.append(feature2D1)
                Data.append(feature2D2)
            elif len(this_line) == L * L:
                # 2D feature
                feature2D = np.asarray(this_line).reshape(L, L)
                Data.append(feature2D)
            else:
                # print(line)
                print('Error!! Unknown length of feature in !!' + _feature_file)
                print('Expected length 0, ' + str(L) + ', or ' + str(L * L) + ' - Found ' + str(len(this_line)))
                sys.exit()

    F = len(Data)
    X = np.zeros((L, L, F))
    for i in range(0, F):
        X[0:L, 0:L, i] = Data[i]
    if np.isnan(np.sum(X)):
        os.system("echo '" + _feature_file + "' >> naninX.txt")
    # print(X.shape)
    return X


def check_single_exists(_file):
    if os.path.exists(_file):
        return True
    else:
        print("This file is missing" + str(_file))
        return False


def check_path_exists(_dncon_file_name,
                      _tr_ros_file_name,
                      _intra_path_file_name,
                      _ss_path_file_name):
    print(_dncon_file_name)
    print(_tr_ros_file_name)
    print(_intra_path_file_name)
    print(_ss_path_file_name)
   

    if check_single_exists(_intra_path_file_name) and check_single_exists(_tr_ros_file_name) and check_single_exists(
            _intra_path_file_name) and check_single_exists(_ss_path_file_name):
        return True
    else:
        return False


def filter_files(_feat_path, tr_ros_path, ss_path, intra_path):
    _distance_maps = []
    _intra_path = []
    _tr_ros = []
    _ss = []
 

    dncon_file_name = _feat_path
    tr_ros_file_name = tr_ros_path
    intra_path_file_name = intra_path
    ss_path_file_name = ss_path

    if os.path.exists(cmap_dir  ):
        print("It is already peresent, so skipping . . . . ")
        exit()

    if check_path_exists(_dncon_file_name=dncon_file_name, _tr_ros_file_name=tr_ros_file_name,
                         _intra_path_file_name=intra_path_file_name, _ss_path_file_name=ss_path_file_name):
        _distance_maps.append(dncon_file_name)
        _intra_path.append(intra_path_file_name)
        _tr_ros.append(tr_ros_file_name)
        _ss.append(ss_path_file_name)

    return sorted(_distance_maps), sorted(_tr_ros), sorted(_ss), sorted(_intra_path)


def fix_pred_map(_input):
    len = _input.shape[0]
    out = np.zeros((len, len))
    for i in range(len):
        for j in range(len):
            temp  = float((_input[i][j] + _input[j][i])) / 2
            out[i][j] =temp
            out[j][i] =temp
    return out


def text_file_reader(_file):
    file = open(_file, "r")
    output_array = []
    if file.mode == 'r':
        output_array = file.read().splitlines()
    file.close()
    return output_array


class my_dataset(data.Dataset):
    def initialize(self, _feat_path, _tr_ros, _ss, _intra, _max_len):
        self.distance_maps, self.tr_ros, self.ss, self.intra_path = filter_files(_feat_path, _tr_ros, _ss, _intra)
        self.size = len(self.distance_maps)
        self.size_intra = len(self.intra_path)
        self.size_tr = len(self.tr_ros)
        self.size_ss = len(self.ss)
        self.MaxLen = _max_len
        self.transform = transforms.Compose([transforms.ToTensor()])

    def __getitem__(self, index):
        path = self.distance_maps[index % self.size]
        path_intra = self.intra_path[index % self.size_intra]
        tr_labels = self.tr_ros[index % self.size_tr]
        ss_8_val = self.ss[index % self.size_ss]

        # sequence_length = ground_truth.squeeze().shape[0]
        intra_feat = np.loadtxt(path_intra)
        sequence_length = intra_feat.squeeze().shape[0]
        content = np.load(tr_labels, allow_pickle=True)
        tr_feature = content.f.arr_0.squeeze()
        feat_dncon = load_features_dncon(_feature_file=path)
        ss_8_feat = load_ss_features_only(_feature_file=ss_8_val)
        name = NAMEOFFILE
        if sequence_length <= 600:
            final_feature = np.zeros((self.MaxLen, self.MaxLen, FEATURES))
            inter_mediate = np.concatenate(
                [tr_feature.squeeze(), feat_dncon.squeeze(), ss_8_feat.squeeze(), np.expand_dims(intra_feat, axis=2)],
                -1)
            fea_len = inter_mediate[0].shape[0]
            for val in range(0, fea_len):
                final_feature[val, 0:fea_len, 0:FEATURES] = inter_mediate[val]
            dist = self.transform(final_feature)

        else:
            inter_mediate = np.concatenate(
                [tr_feature.squeeze(), feat_dncon.squeeze(), ss_8_feat.squeeze(), np.expand_dims(intra_feat, axis=2)],
                -1)
            dist = self.transform(inter_mediate)

        return {'feat': dist, 'sequence_length': sequence_length,
                'name': name}

    def __len__(self):
        return self.size


nThreads = 6

val_dataset = my_dataset()
val_dataset.initialize(_feat_path=feature_path, _ss=ss_path, _intra=intra_path, _tr_ros=tr_path, _max_len=MAX_LENGTH)
val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=BATCH_SIZE, num_workers=nThreads)
print(len(val_dataloader))


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


len_prot = 600
model = resnet_model.ResNet_custom(img_channel=FEATURES, num_classes=len_prot * len_prot, _depth=RESNET_DEPTH)
print("VALIDATIOn AREA ")
# len_prot = data['sequence_length']
# model = rough_copy.ResNet_custom(img_channel=FEATURES, num_classes=len_prot * len_prot, _depth=RESNET_DEPTH)

model.cuda()
last_weight = model_path
checkpoint = torch.load(last_weight)
model.load_state_dict(checkpoint['model'])
with torch.no_grad():
    for i, data in enumerate(val_dataloader):
        features = data['feat'].float().cuda()
        real_sequence_length = data['sequence_length'].int().cuda()
        model.eval()
        print(data['name'])
        output_val = model(features)
        output_final = torch.squeeze(output_val, -1).detach().cpu().clone().numpy().squeeze()
        mini_batch_size = BATCH_SIZE
        shape_label_array = real_sequence_length.detach().cpu().clone().numpy().squeeze()
        
        print(output_final.shape)
        if os.path.exists(cmap_dir  ):
            continue
        shape_label = shape_label_array
        padded_predicted_label = output_final
        if real_sequence_length <= 600:
            unpadded_predicted_label = np.zeros((shape_label, shape_label))
            unpadded_true_label = np.zeros((shape_label, shape_label))
            for val in range(0, shape_label):
                unpadded_predicted_label[val] = padded_predicted_label[val][0:shape_label]
        else:
            unpadded_predicted_label = output_final
        print(cmap_dir)
        unpadded_true_label = fix_pred_map(unpadded_predicted_label)
        np.savetxt(cmap_dir , unpadded_predicted_label)


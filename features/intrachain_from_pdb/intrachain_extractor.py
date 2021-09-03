#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys
import numpy as np
from readPDBColumns import readPDB,readAtom,write2File,contents2Info,addColumn,reassembleLines,getChain

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
        _cmap[int(values[0]) - 1][int(values[1]) - 1] = 1
        _cmap[int(values[1]) - 1][int(values[0]) - 1] = 1
    return _cmap

def getCB(atom_list):
    new_list=[]
    #print(atom_list)
    prev_res_num=atom_list[0]["res_num"].strip()
    added=False
    keep={}
    for tup in atom_list:
        if (prev_res_num==tup["res_num"].strip() and added==True):
            keep={}
            continue
        if (prev_res_num!=tup["res_num"].strip() and added==False): #No CB found. So add the CA
                new_list.append(keep)
                keep={}
                added=False
                prev_res_num=tup["res_num"].strip()
        if (prev_res_num!=tup["res_num"].strip() and added==True): #Reached the next residue
                keep={}
                added=False
                prev_res_num=tup["res_num"].strip()
        if (prev_res_num==tup["res_num"].strip() and added==False):

            if ("CA" in tup["atom_name"]):
                keep=tup
            if ("GLY" in tup["res_name"] and "CA" in tup["atom_name"]):
                new_list.append(tup)
                added=True
                prev_res_num=tup["res_num"].strip()
                continue
            else:
                if (tup["atom_name"].strip()=="CB"):
                    new_list.append(tup)
                    added=True
                    prev_res_num=tup["res_num"].strip()
                    continue
    if (added==False): new_list.append(keep)
    #print (new_list[-1])
    return new_list


def createDistanceMap(chainA,chainB):
    lenA=len(chainA)
    lenB=len(chainB)
    distmap=np.zeros((L+1,L+1))
    #print(distmap.shape)
    atom_list_A=[]
    atom_list_B=[]
    for i in range(lenA):
        infoA=chainA[i]
        chain_A=infoA["chain"]
        res_num_A=infoA["res_num"]
        atom_num_A=infoA["serial"]
        residue_A=infoA["res_name"]
        atom_A=infoA["atom_name"]
        fasta_res_num_A=infoA["res_num"]
        atom_list_A.append((chain_A,fasta_res_num_A,res_num_A,atom_num_A,residue_A,atom_A))
        x1=float(infoA["x"])
        y1=float(infoA["y"])
        z1=float(infoA["z"])
        for j in range(i,lenB):
            #print(j)
            infoB=chainB[j]
            chain_B=infoB["chain"]
            res_num_B=infoB["res_num"]
            atom_num_B=infoB["serial"]
            residue_B=infoB["res_name"]
            atom_B=infoB["atom_name"]
            fasta_res_num_B=infoB["res_num"]
            x2=float(infoB["x"])
            y2=float(infoB["y"])
            z2=float(infoB["z"])


            atom_list_B.append((chain_B,fasta_res_num_B,res_num_B,atom_num_B,residue_B,atom_B))
            distmap[int(res_num_A)][int(res_num_B)]=np.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2))
            distmap[int(res_num_B)][int(res_num_A)]=np.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2))
    return distmap



def createDistDistribution(distmap,threshold=5):
#creates a distance distribution of those atoms whose distances are less than the threshold distance
    (lA,lB)=distmap.shape
    distribution=[]
    rr_distribution=[]
    for i in range (1,lA): #changed from 0 to 1
        for j in range (i+1,lB):
            #if (i==j): continue
            if (threshold==0):
                distribution.append(str(i)+" "+str(j)+" 0 "+str(threshold)+" "+str(distmap[i][j])+"\n")
                rr_distribution.append(str(i)+" "+str(j)+" 0 "+str(threshold)+" "+str((1/distmap[i][j])+0.5)+"\n")
            else:
                if (distmap[i][j]<=threshold and distmap[i][j]!=0):
                    distribution.append(str(i)+" "+str(j)+" 0 "+str(threshold)+" "+str(distmap[i][j])+"\n")
                    rr_distribution.append(str(i)+" "+str(j)+" 0 "+str(threshold)+" "+str((1/distmap[i][j])+0.5)+"\n")


    return distribution,rr_distribution#,distribution_list



def read_fastaonly(_input):
    array = []
    file = open(_input, "r")
    if file.mode == 'r':
        array = file.read().splitlines()
    file.close()

    fasta =   array[1] + "\n"


    return fasta

pdbfilename=sys.argv[1]
fasta= read_fastaonly(sys.argv[2]).strip()
outfile=sys.argv[3]
# pdbfilename=  "/home/rajroy/dncon2_env/T0893A.pdb"
# fasta=read_fastaonly("/home/rajroy/dncon2_env/T0893.fasta").strip()
# outfile="/home/rajroy/"

dist=8
chain_dict=readPDB(pdbfilename)
split_contents_A=contents2Info(readPDB(pdbfilename))
split_contents_B=contents2Info(readPDB(pdbfilename))
chain_1=getChain(pdbfilename)
chain_2=getChain(pdbfilename)


cb_list=getCB(split_contents_A)
L=len(fasta)
if not len(cb_list) == L:
    print("ERROR:  THE LENGTH OF THE FASTA AND THE PDB IS NO SAME")
    exit()

distmap=createDistanceMap(getCB(split_contents_A),getCB(split_contents_B))

distribution,rr_distribution=createDistDistribution(distmap,float(dist))

outfile_dist=outfile+os.path.basename(pdbfilename).split(".")[0]+"_bb"+".txt"
print(outfile)
outfile_rr=outfile+"_"+chain_1+chain_2+".rr"
distribution.insert(0,fasta+"\n")
rr_distribution.insert(0,fasta+"\n")
with open (outfile_dist,"w") as f:
    f.writelines(distribution)

values = rr2cmap(outfile_dist)
final_file = outfile+ (os.path.basename(pdbfilename).split(".")[0])+"_intra.cmap"
# with open (outfile_rr,"w") as f:
#     f.writelines(rr_distribution)

if not os.path.exists(final_file):
        out_str = ""
        for v in values:
            temp_str = ""
            for inner_val in v:
                temp_str = temp_str+str(float(inner_val))+" "
            print(temp_str)
            out_str=out_str+temp_str+"\n"
        writecmaps(file=final_file,contents=out_str)
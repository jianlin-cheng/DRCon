

# The DRCon, homodimer interchain predictor requires 4 Features, as follows:

**(1) DNCON2 Features**

**(2) Intrachain contact maps**

**(3) 8-state secondary structures by SCRATCH**

**(4) trRosetta Features**


# Details for features generation

**(1) To Generate the Dncon2 Features follow guideline from here:  https://github.com/jianlin-cheng/DeepComplex**
After seting them up and generating the features and use the "feat" file inside it.
e.g feat-11AS.txt or feat-<target_id>.txt

**(2) For extracting the true intrachain you may use the script inside "intrachain_from_pdb" or generate them using some tools and use batch_rr_2_cmap.py to convert it to cmaps**
Convert pdb to intrachain distance
```
python pdb2Distancemonomer.py ./4FBL.pdb ./4FBL.fasta ./features
```
then place all the rr in a directory and choose a directory to place the cmaps
```
python batch_rr_2_cmap  ./input_dir/ ./ouput_dir/
```

**(3) FOR 8 state secondary features  use SCRATCH-1D_1.1:**
Generate them using scratch and use the script "SS8_onehot.py" to get the one-hot encoded feature files
```
Usage : python ss8_onehot.py <input_file_name> <output_dir>
e.g python ss8_onehot.py ./4FBL.ss8 ./
```

**(4) For trRosetta Features**
Use this link for setting it up : https://github.com/gjoni/trRosetta
To generate the trRosetta features you will  need alignment file in a3m format, you may generate them sepeartly or use the file inside the alignment file of the DNCON2 features.
Inside the DNCON2 aligment file there is a file called result.txt open it and use the corresponding "a3m" of the final ".aln"
```
e.g of the text inside results.txt file
"cp jhm-1e-10.aln T1087o.aln"
Therefore use the jhm-1e-10.a3m for trRosetta features
```


Place the predict_2.py insisde the trRosetta_features_generator inside the directory "netowrk" of the trRosetta
```
Usage : python predict_2.py -m ./model2019_07 ./example/T1001.a3m ./example/
```

# Finally run the predictor.
```
USAGE: python DRCON_pred.py <MODEL_PATH> <OUTPUT_PATH> <TARGET_ID> <DNCON Feature path> <INTRACHAIN Feature path> <SS8 Feature path> <trRoseetta Feature path>
e.g
python DRCON_pred.py /gpfs/alpine/proj-shared/bif132/raj/codes/pytroch_codes/updated_history/weighths_82 /gpfs/alpine/proj-shared/bif132/raj/codes/pytroch_codes/ 3GWR /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/dncon_feat_only/feat-3GWR.txt /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/intra_cmap/3GWR.cmap /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/ss8_one_hot/3GWR.feat_ss8 /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/tr_features/3GWR.npz
```




# TESTED ON THE FOLLOWING LIBRARY PACKAGE
python                    3.8.8                h836d2c2_4

pytorch                   1.7.1           cuda10.2_py38_2

pytorch-base              1.7.1           cuda10.2_py38_8

torchtext                 0.8.1                    py38_4

torchvision               0.8.2           cuda10.2_py38_0

torchvision-base          0.8.2           cuda10.2_py38_6


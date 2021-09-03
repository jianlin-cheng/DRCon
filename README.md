# DRCon
Deep dilated convolutional residual neural network for predicting interchain contacts of protein homodimers


# First Time Setup
**(1) Install the DNCON2 follwoing this github repository (https://github.com/multicom-toolbox/DNCON2)**


**(2) Install trRosetta following this github repository (https://github.com/gjoni/trRosetta)**
      
- Once installing is done :  Copy the file /DRCon/features/trRosetta_features_generator/predict_2.py into the directory "/trRosetta/network/" of the trRosetta 
 
 
 # Running DRCon

The DRCon, homodimer interchain predictor requires 4 features to predict the interchain contacts, they are as follows:

**(1) DNCON2 Features: This is the output of running DNCON2 (Step 1 of first time setup)**

**(2) Intrachain contact maps: This can be generated from pdb or someother software can used to generate the contact maps**

**(3) 8-state secondary structures features by SCRATCH: This will be generated during dncon2 features generation**

**(4) trRosetta Features:This feature require alignment in a3m file and a3m file is also generated during dncon2 feature generation similarly a3m file from somether sources can be used**



# Details for features generation

**(1) To Generate the Dncon2 Features follow guideline from here:  https://github.com/jianlin-cheng/DeepComplex**

After seting them up and generating the features and use the "feat" file inside it.
e.g feat-11AS.txt or feat-<target_id>.txt

**(2) For extracting the intrachain you may use the script inside "intrachain_from_pdb" or generate them using some tools and convert it to cmaps**

Convert pdb to intrachain distance

```
python intrachain_extractor.py <input_atom/pdb file > <fasta of the input file> <output file >

python intrachain_extractor.py ./example/3GWRA.atom ./example/3GWRA.fasta ~/

```
Alternatively direct intrachain contact map from any other software can also used but applying a cutoff (e.g. 0.5 ) may increase the performance 

```
python intrachain_extractor.py <input cmap file> <cut off value (0 to 1.0) >  <output file>
python intrachain_extractor.py /cutoff_cmap.py ~/137L.intra_cmap 0.5 ~/

```


**(3) FOR 8 state secondary features  use SCRATCH-1D_1.1:**
SS8 files generated during making of DNCON2 features, it is located inside the "ss_sa" directory of the DNCON2_features file. And then use the script "SS8_onehot.py" to get the one-hot encoded feature files
```
Usage : python ss8_onehot.py <input_file_name> <output_dir>
e.g python ss8_onehot.py ./4FBL.ss8 ./
```

**(4) For trRosetta Features**

Use this link for setting it up : https://github.com/gjoni/trRosetta

To generate the trRosetta features you will need alignment file in a3m format, you may generate them sepeartly or use the file inside the alignment file of the DNCON2 features.
Inside the DNCON2 aligment file there is a file called result.txt, which contains name of the final alignment file in aln format. Use the corresponding "a3m" file  of the final ".aln"
```
e.g of the text inside results.txt file
"cp jhm-1e-10.aln T1087o.aln"
Therefore use the jhm-1e-10.a3m for trRosetta features
```


Copy the predict_2.py from the "trRosetta_features_generator" into the directory "network" of the trRosetta
```
Usage : python predict_2.py -m <tr_rosetta weight file > <input a3m file > <output directory>

Usage : python predict_2.py -m ./model2019_07 ./example/T1001.a3m ./example/
```

# Finally run the predictor.
```
USAGE: python DRCON_pred.py <MODEL_PATH> <OUTPUT_PATH> <TARGET_ID> <DNCON Feature path> <INTRACHAIN Feature path> <SS8 Feature path> <trRoseetta Feature path>
e.g
python DRCON_pred.py /gpfs/alpine/proj-shared/bif132/raj/codes/pytroch_codes/updated_history/weighths_82 /gpfs/alpine/proj-shared/bif132/raj/codes/pytroch_codes/ 3GWR /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/dncon_feat_only/feat-3GWR.txt /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/intra_cmap/3GWR.cmap /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/ss8_one_hot/3GWR.feat_ss8 /gpfs/alpine/proj-shared/bif132/raj/dimer/Deephomo_data/tr_features/3GWR.npz
```




# TESTED ON THE FOLLOWING LIBRARY PACKAGE
python                    3.8.8               

pytorch                   1.7.1            

pytorch-base              1.7.1          

torchtext                 0.8.1            

torchvision               0.8.2        

torchvision-base          0.8.2          





#DATA Avaiability
```
(1) Labels : http://sysbio.rnet.missouri.edu/bml_data/protein_complex_interaction/DeepComplexProject/HOMO_STD_DATA/Y-Labels/

(2) Atom :  http://sysbio.rnet.missouri.edu/bml_data/protein_complex_interaction/DeepComplexProject/HOMO_STD_DATA/homo_std_reindexed_atom.zip

(3) Fasta : http://sysbio.rnet.missouri.edu/bml_data/protein_complex_interaction/DeepComplexProject/HOMO_STD_DATA/fastas/
```

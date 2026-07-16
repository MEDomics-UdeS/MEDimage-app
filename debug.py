import os
from pathlib import Path

import pandas as pd

import pickle
import joblib

path_sts = Path("/Users/chum/Documents/MEDomics/workspace/teest")
with open(path_sts / "STS-McGill-001__CT.CTscan.npy", "rb") as f:
    test = pickle.load(f)
    
import MEDiml


path_npy = Path("/Users/chum/Documents/MEDomics/workspace/npy")
path_dicoms = Path("/Users/chum/Documents/MEDomics/workspace/npy")
path_to_params = Path("/Users/chum/Documents/MEDomics/workspace/MEDscan-Tutorial.json")
path_csv_bmets = Path("/Users/chum/Documents/MEDomics/workspace/roiNames_GTV.csv")
path_pred_doses = Path("")
path_save = Path("/Users/chum/Documents/MEDomics/workspace/DATA")


batch_extractor = MEDiml.biomarkers.BatchExtractor(
    path_read=path_npy,
    path_csv=path_csv_bmets,
    path_params=path_to_params,
    path_save=path_save,
)

batch_extractor.compute_radiomics()
 
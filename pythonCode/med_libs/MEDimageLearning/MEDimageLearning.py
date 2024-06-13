import os
import pprint
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import jupytext
import pandas as pd
from numpyencoder import NumpyEncoder

pp = pprint.PrettyPrinter(width=1)  # allow pretty print of datatypes in console

import MEDimage

from .utils import *


class MEDimageLearning:
    def __init__(self, json_config: dict) -> None:
        self.json_config = json_config
        self._progress = {'currentLabel': '', 'now': 0.0}
    
    def __round_dict(self, dict, decimals):
        for key, value in dict.items():
            if (type(value) is list):
                dict[key] = [round(x, decimals) for x in value]
            else:
                dict[key] = round(value, decimals)

        return dict
    
    def generate_all_pips(self, id: str, node_content, pip, json_scene, pips, counter):
        # -------------------------------------------------- NODE ADD ---------------------------------------------------
        pip.append(id)  # Current node added to pip

        # ---------------------------------------------- NEXT NODES COMPUTE ----------------------------------------------
        # NO OUPUT CONNECTION
        if not "output_1" in node_content["outputs"]:  # if no ouput connection
            pips.append(deepcopy(pip))  # Add the current pip to pips
            return pip

        # ONE OUPUT CONNECTION
        elif len(node_content["outputs"]["output_1"]["connections"]) == 1:
            out_node_id = node_content["outputs"]["output_1"]["connections"][0]["node"]
            out_node_content = get_node_content(out_node_id, json_scene)
            pip = self.generate_all_pips(out_node_id, out_node_content, pip, json_scene, pips, counter)

        # MORE ONE OUPUT CONNECTION
        else:
            connections = node_content["outputs"]["output_1"]["connections"]  # output connections of last node added to pip
            for connection in connections:
                pip_copy = deepcopy(pip)  # Copy the current pip
                out_node_id = connection["node"]  # Retrieve all nodes connected to the current node output
                out_node_content = get_node_content(out_node_id, json_scene)  # Retrieve all nodes content
                pip_copy = self.generate_all_pips(out_node_id, out_node_content, pip_copy, json_scene, pips, counter)

        return pip
    
    def execute_pips(self, pips, json_scene):
        # Init RUNS dict for store instances and logs (xxx_obj)
        pips_obj = {}

        # Init results dict for result response (xxx_res)
        pips_res = {}
        scan_res = {}
        filename_loaded = ""
        results_avg = []
        analysis_dict = {}
        splitted_data = False

        # ------------------------------------------ PIP EXECUTION ------------------------------------------
        for pip_idx, pip in enumerate(pips):

            pip_name = "pipeline" + str(pip_idx+1)

            self.set_progress(now=0.0, label=f"Pipeline {pip_idx+1} execution")

            print("\n\n!!!!!!!!!!!!!!!!!! New pipeline execution !!!!!!!!!!!!!!!!!! \n --> Pip : ", pip)

            # Init object and variables for new pipeline
            pip_obj = {}
            pip_name_obj = ""
            pip_res = {}
            pip_name_res = "pip"
            holdout_test = False
            cleaned_data = False
            normalized_features = False
            reduced_features = False
            designed_experiment = False
            loaded_data = False
            split_counter = 0
            saved_results = False
            
            # ------------------------------------------ NODE EXECUTION ------------------------------------------
            while True:
                for node in pip:
                    content = get_node_content(node, json_scene)
                    print("\n\n\n///////////////// CURRENT NODE :", content["name"], "-", node, " /////////////////")

                    # Update RUNS dict for store instances and logs (xxx_obj)
                    update_pip = False
                    pip_name_obj += node
                    id_obj = {}
                    id_obj["type"] = content["name"]
                    id_obj["settings"] = content["data"]

                    # Update results dict for result response (xxx_res)
                    pip_name_res += "/" + node

                    # ------------------------------------------ HOME ------------------------------------------
                    # Split
                    if (content["name"].lower() == "split"):
                        print("\n********SPLIT execution********")
                        try:
                            if not splitted_data:
                                # Retrieve data from json request
                                if "path_outcome_file" in content["data"].keys() and content["data"]["path_outcome_file"] != "":
                                    path_outcome_file = Path(content["data"]["path_outcome_file"])
                                else:
                                    return {"error": "Split: Path to outcome file is not given!"}
                                if "path_save_experiments" in content["data"].keys() and content["data"]["path_save_experiments"] != "":
                                    path_save_experiments = Path(content["data"]["path_save_experiments"])
                                else:
                                    return {"error":  "Split: Path to save experiments is not given!"}
                                if "outcome_name" in content["data"].keys() and content["data"]["outcome_name"] != "":
                                    outcome_name = content["data"]["outcome_name"]
                                else:
                                    return {"error":  "Split: Outcome name is not given!"}
                                if "method" in content["data"].keys() and content["data"]["method"] != "":
                                    method = content["data"]["method"]
                                else:
                                    return {"error":  "Split: Method is not given!"}
                                if method == "all_learn":
                                    holdout_test = False
                                else:
                                    holdout_test = True

                                # Reset progress
                                self.set_progress(now=0.0, label=f"Pip {str(pip_idx+1)} | Spliting data")

                                # Generate the machine learning experiment
                                path_study, _ = MEDimage.learning.ml_utils.create_holdout_set(
                                    path_outcome_file=path_outcome_file,
                                    path_save_experiments=path_save_experiments,
                                    outcome_name=outcome_name,
                                    method=method
                                )
                                splitted_data = True
                                self.set_progress(now=5)
                        except Exception as e:
                            return {"error": str(e)}

                    # Design
                    if (content["name"].lower() == "design"):
                        print("\n********DESIGN execution********")
                        try:
                            if not designed_experiment:
                                self.set_progress(label=f"Pip {str(pip_idx+1)} | Designing experiment")
                                # Initialization
                                path_settings = Path.cwd() / "flask_server" / "learning_MEDimage" / "settings"
                                desing_settings = {}

                                # Retrieve data from json request
                                if splitted_data and path_study is None:
                                    if "path_study" in content["data"].keys() and content["data"]["path_study"] != "":
                                        path_study = Path(content["data"]["path_study"])
                                    else:
                                        return {"error":  "Desing: Path to study is not given!"}
                                if "expName" in content["data"].keys() and content["data"]["expName"] != "":
                                    experiment_label = content["data"]["expName"]
                                else:
                                    return {"error":  "Desing: Experiment label is not given!"}
                                
                                # Fill design settings
                                desing_settings['design'] = content["data"]

                                # Initialize the DesignExperiment class
                                experiment = MEDimage.learning.DesignExperiment(path_study, path_settings, experiment_label)

                                # Generate the machine learning experiment
                                tests_dict = experiment.create_experiment(desing_settings)

                                paths_splits = []
                                for run in tests_dict.keys():
                                    paths_splits.append(tests_dict[run])
                                
                                # Set up the split counter
                                split_counter = 0
                                designed_experiment = True
                                self.set_progress(now=10)
                        except Exception as e:
                            return {"error": str(e)}

                    # Model training/testing part
                    if designed_experiment:            
                        # Data
                        if (content["name"].lower() == "data"):
                            print("\n********DATA execution********")
                            try:
                                if not designed_experiment:
                                    return {"error":  "Data: Experiment must be designed first! Re-organize nodes."}
                                
                                # Update progress
                                self.set_progress(label=f"Pip {str(pip_idx+1)} | Split {split_counter+1} | Loading data")
                                
                                # --> A. Initialization phase
                                learner = MEDimage.learning.RadiomicsLearner(path_study=path_study, path_settings=Path.cwd(), experiment_label=experiment_label)

                                # Load the test dictionary and machine learning information
                                path_ml = paths_splits[split_counter]
                                ml_dict_paths = MEDimage.utils.load_json(path_ml)      # Test information dictionary

                                # Machine learning information dictionary
                                ml_info_dict = dict()

                                # Training and test patients
                                ml_info_dict['patientsTrain'] = MEDimage.utils.load_json(ml_dict_paths['patientsTrain'])
                                ml_info_dict['patientsTest'] = MEDimage.utils.load_json(ml_dict_paths['patientsTest'])

                                # Outcome table for training and test patients
                                outcome_table = pd.read_csv(ml_dict_paths['outcomes'], index_col=0)
                                ml_info_dict['outcome_table_binary'] = outcome_table.iloc[:, [0]]
                                if outcome_table.shape[1] == 2:
                                    ml_info_dict['outcome_table_time'] = outcome_table.iloc[:, [1]]
                                
                                # Machine learning dictionary
                                ml_info_dict['path_results'] = ml_dict_paths['results']
                                del outcome_table

                                # Machine learning assets
                                patients_train = ml_info_dict['patientsTrain']
                                patients_test = ml_info_dict['patientsTest']
                                patients_holdout = MEDimage.utils.load_json(path_study / 'patientsHoldOut.json') if holdout_test else None
                                outcome_table_binary = ml_info_dict['outcome_table_binary']
                                path_results = ml_info_dict['path_results']
                                patient_ids = list(outcome_table_binary.index)
                                outcome_table_binary_training = outcome_table_binary.loc[patients_train]
                                flags_preprocessing = []
                                flags_preprocessing_test = []
                                rad_tables_learning = list()

                                # --> B. Pre-processing phase
                                # B.1. Pre-processing initialization, settings tables paths
                                rad_var_struct = dict()

                                # For each variable, organize the option in the ML dictionary
                                if "nameType" in content["data"].keys() and content["data"]["nameType"] != "":
                                    name_type = content["data"]["nameType"]
                                else:
                                    name_type = "radiomics"
                                # Radiomics variables
                                if 'radiomics' in name_type.lower():
                                    # Get radiomics features folder
                                    if "path" in content["data"].keys() and content["data"]["path"] != "":
                                        path_features = Path(content["data"]["path"])
                                    else:
                                        return {"error":  "Data: Path to radiomics features is not given!"}
                                    if "featuresFiles" in content["data"].keys() and content["data"]["featuresFiles"] != "":
                                        features_files = content["data"]["featuresFiles"]
                                        for file in features_files:
                                            if not file.endswith('.csv'):
                                                return {"error":  "Data node: Only csv files are supported!"}
                                    else:
                                        return {"error":  "Data node: No features files were selected!"}
                                    
                                    # Initialize dict to hold all paths to radiomics features (csv and txt files)
                                    path = dict() 
                                    for idx, feature_file in enumerate(features_files):
                                        rad_tab_x = {}
                                        name_tab = 'radTab' + str(idx+1)
                                        rad_tab_x['csv'] = Path(path_features / feature_file)
                                        rad_tab_x['txt'] = Path(path_features / (feature_file.split('.')[0] + '.txt'))
                                        rad_tab_x['type'] = feature_file.split('__')[1].split('_')[0] if '__' in feature_file else 'None'

                                        # check if file exist
                                        if not rad_tab_x['csv'].exists():
                                            raise FileNotFoundError(f"File {rad_tab_x['csv']} does not exist.")
                                        if not rad_tab_x['txt'].exists():
                                            raise FileNotFoundError(f"File {rad_tab_x['txt']} does not exist.")
                                        
                                        path[name_tab] = rad_tab_x
                                        
                                        # Add path to ml dict for the current variable
                                        rad_var_struct['path'] = path
                                    
                                    # Update
                                    loaded_data = True
                                    self.set_progress(now=round(self._progress['now'] + 100/len(paths_splits)/5))

                                # Clinical or other variables (For ex: Volume)
                                else:
                                    return {"error":  "Variable type not implemented yet, only Radiomics variables are supported!"}
                            except Exception as e:
                                return {"error": str(e)}

                        # Cleaning
                        if (content["name"].lower() == "cleaning"):
                            try:
                                if not loaded_data:
                                    return {"error":  "Cleaning: Data must be loaded first! Use Data node."}
                                if path_study is None:
                                    return {"error":  "Cleaning: Path to study is not given!"}
                                if experiment_label is None:
                                    return {"error":  "Cleaning: Experiment label is not given!"}

                                # Update progress
                                self.set_progress(label=f"Pip {str(pip_idx+1)} | Split {split_counter+1} | Cleaning data")

                                # Pre-processing
                                for item in rad_var_struct['path'].values():
                                    # Loading the table
                                    path_radiomics_csv = item['csv']
                                    path_radiomics_txt = item['txt']
                                    image_type = item['type']
                                    rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)

                                    # Avoid future bugs (caused in Windows)
                                    if type(rad_table_learning.Properties['Description']) not in [str, Path]:
                                        rad_table_learning.Properties['Description'] = str(rad_table_learning.Properties['Description'])

                                    # Data cleaning
                                    data_cln_method = list(content["data"].keys())[0]
                                    cleaning_dict = content['data'][data_cln_method]['feature']['continuous']
                                    data_cleaner = MEDimage.learning.DataCleaner(rad_table_learning)
                                    rad_table_learning = data_cleaner(cleaning_dict)
                                    if rad_table_learning is None:
                                        continue
                                    rad_tables_learning.append(rad_table_learning)
                                
                                # Finalization steps
                                flags_preprocessing.append("var_datacleaning")
                                flags_preprocessing_test.append("var_datacleaning")
                                cleaned_data = True
                                self.set_progress(now=round(self._progress['now'] + 100/len(paths_splits)/5))
                            except Exception as e:
                                return {"error": str(e)}
                        
                        if (content["name"].lower() == "normalization"):
                            try:
                                if not loaded_data:
                                    return {"error":  "Cleaning: Data must be loaded first! Use Data node."}
                                if "method" in content["data"].keys() and content["data"]["method"] != "":
                                    normalization_method = content["data"]["method"]
                                else:
                                    normalization_method = ""
                                
                                # Update progress
                                self.set_progress(label=f"Pip {str(pip_idx+1)} | Split {split_counter+1} | Normalizing data")

                                # If there was no cleaning step, the data must be loaded
                                if not cleaned_data:
                                    for item in rad_var_struct['path'].values():
                                        # Loading the table
                                        path_radiomics_csv = item['csv']
                                        path_radiomics_txt = item['txt']
                                        image_type = item['type']
                                        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)
                                        rad_tables_learning.append(rad_table_learning)

                                # Start features normalization for each table
                                for rad_table_learning in rad_tables_learning:
                                    # Some information must be stored to re-apply combat for testing data
                                    if 'combat' in normalization_method.lower():
                                        # Training data
                                        rad_table_learning.Properties['userData']['normalization'] = dict()
                                        rad_table_learning.Properties['userData']['normalization']['original_data'] = dict()
                                        rad_table_learning.Properties['userData']['normalization']['original_data']['path_radiomics_csv'] = str(path_radiomics_csv)
                                        rad_table_learning.Properties['userData']['normalization']['original_data']['path_radiomics_txt'] = str(path_radiomics_txt)
                                        rad_table_learning.Properties['userData']['normalization']['original_data']['image_type'] = str(image_type)
                                        rad_table_learning.Properties['userData']['normalization']['original_data']['patient_ids'] = patient_ids
                                        if cleaned_data:
                                            data_cln_method = data_cln_method
                                            rad_table_learning.Properties['userData']['normalization']['original_data']['datacleaning_method'] = data_cln_method
                                        
                                        # Apply ComBat
                                        normalization = MEDimage.learning.Normalization('combat')
                                        rad_table_learning = normalization.apply_combat(variable_table=rad_table_learning)  # Training data
                                    else:
                                        return {"error":  f"Normalization: method {normalization_method} not implemented yet!"}
                                    
                                self.set_progress(now=round(self._progress['now'] + 100/len(paths_splits)/5))
                                normalized_features = True
                            except Exception as e:
                                return {"error": str(e)}

                        if (content["name"].lower() == "feature_reduction"):
                            # Load data if cleaning step or normalization step was not performed
                            try:
                                if not loaded_data:
                                    return {"error":  "Cleaning: Data must be loaded first! Use Data node."}
                                if not cleaned_data and not normalized_features:
                                    for item in rad_var_struct['path'].values():
                                        # Loading the table
                                        path_radiomics_csv = item['csv']
                                        path_radiomics_txt = item['txt']
                                        image_type = item['type']
                                        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)
                                        rad_tables_learning.append(rad_table_learning)

                                # Update progress
                                self.set_progress(label=f"Pip {str(pip_idx+1)} | Split {split_counter+1} | Reducing data")

                                # Seperate training and testing data before feature set reduction
                                rad_tables_testing = deepcopy(rad_tables_learning)
                                rad_tables_training = []
                                for rad_tab in rad_tables_learning:
                                    patients_ids = MEDimage.learning.ml_utils.intersect(patients_train, list(rad_tab.index))
                                    rad_tables_training.append(deepcopy(rad_tab.loc[patients_ids]))

                                # Deepcopy properties
                                temp_properties = list()
                                for rad_tab in rad_tables_testing:
                                    temp_properties.append(deepcopy(rad_tab.Properties))
                                
                                # Feature set reduction
                                if "method" in content["data"].keys() and content["data"]["method"] != "":
                                    f_set_reduction_method = content["data"]["method"]
                                else:
                                    f_set_reduction_method = "FDA"

                                # Check if method is FDA (the only one implemented for the moment)
                                if f_set_reduction_method.lower() != "fda":
                                    return {"error":  "Feature Reduction: Method not implemented yet (check FSR class)!"}
                                
                                # Prepare settings dict
                                fsr_dict = dict()
                                fsr_dict['fSetReduction'] = dict()
                                fsr_dict['fSetReduction']['FDA'] = content["data"]['FDA']

                                # Initialize the FSR class
                                fsr = MEDimage.learning.FSR(f_set_reduction_method)
                                
                                # Apply FDA
                                rad_tables_training = fsr.apply_fsr(
                                    fsr_dict, 
                                    rad_tables_training, 
                                    outcome_table_binary_training, 
                                    path_save_logging=path_results
                                )
                            
                                # Finalize processing tables
                                # Re-assign properties
                                for i in range(len(rad_tables_testing)):
                                    rad_tables_testing[i].Properties = temp_properties[i]
                                del temp_properties

                                # Finalization steps
                                rad_tables_training.Properties['userData']['flags_preprocessing'] = flags_preprocessing
                                rad_tables_testing = MEDimage.learning.ml_utils.combine_rad_tables(rad_tables_testing)
                                rad_tables_testing.Properties['userData']['flags_processing'] = flags_preprocessing_test
                                reduced_features = True
                                self.set_progress(now=round(self._progress['now'] + 100/len(paths_splits)/5))
                            except Exception as e:
                                return {"error": str(e)}

                        # --------------------------- MODEL TRAINING ---------------------------
                        if content["name"].lower() == "radiomics_learner":
                            # If no cleaning, normalization or feature set reduction step was performed, the data must be loaded
                            try:
                                if not loaded_data:
                                    return {"error":  "Cleaning: Data must be loaded first! Use Data node."}
                                if not cleaned_data and not normalized_features and not reduced_features:
                                    for item in rad_var_struct['path'].values():
                                        # Loading the table
                                        path_radiomics_csv = item['csv']
                                        path_radiomics_txt = item['txt']
                                        image_type = item['type']
                                        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)
                                        rad_tables_learning.append(rad_table_learning)
                                
                                # Update progress
                                self.set_progress(label=f"Pip {str(pip_idx+1)} | Split {split_counter+1} | Model training")

                                # Seperate training and testing if no feature set reduction step was performed
                                if not reduced_features:
                                    rad_tables_testing = deepcopy(rad_tables_learning)
                                    rad_tables_training = []
                                    for rad_tab in rad_tables_learning:
                                        patients_ids = MEDimage.learning.ml_utils.intersect(patients_train, list(rad_tab.index))
                                        rad_tables_training.append(deepcopy(rad_tab.loc[patients_ids]))
                                
                                # B.2. Pre-learning initialization
                                # Patient definitions (training and test sets)
                                patient_ids = list(outcome_table_binary.index)
                                patients_train = MEDimage.learning.ml_utils.intersect(MEDimage.learning.ml_utils.intersect(patient_ids, patients_train), rad_tables_training.index)
                                patients_test = MEDimage.learning.ml_utils.intersect(MEDimage.learning.ml_utils.intersect(patient_ids, patients_test), rad_tables_testing.index)
                                patients_holdout = MEDimage.learning.ml_utils.intersect(patient_ids, patients_holdout) if holdout_test else None

                                # Initializing outcome tables for training and test sets
                                outcome_table_binary_train = outcome_table_binary.loc[patients_train, :]
                                outcome_table_binary_test = outcome_table_binary.loc[patients_test, :]
                                outcome_table_binary_holdout = outcome_table_binary.loc[patients_holdout, :] if holdout_test else None

                                # Initializing XGBoost model settings
                                if "model" in content["data"].keys() and content["data"]["model"] is not None:
                                    model_name = content["data"]["model"]
                                if "varImportanceThreshold" in content["data"][model_name].keys() and content["data"][model_name]["varImportanceThreshold"] is not None:
                                    var_importance_threshold = content["data"][model_name]["varImportanceThreshold"]
                                else:
                                    return {"error":  "Radiomics learner: Radiomics learner: variable importance threshold not provided"}
                                if "optimalThreshold" in content["data"][model_name].keys() and content["data"][model_name]["optimalThreshold"] is not None:
                                    optimal_threshold = content["data"][model_name]["optimalThreshold"]
                                else:
                                    optimal_threshold = None
                                if "optimizationMetric" in content["data"][model_name].keys() and content["data"][model_name]["optimizationMetric"] is not None:
                                    optimization_metric = content["data"][model_name]["optimizationMetric"]
                                else:
                                    return {"error":  "Radiomics learner: Optimization metric was not provided"}
                                if "method" in content["data"][model_name].keys() and content["data"][model_name]["method"] is not None:
                                    method = content["data"][model_name]["method"]
                                else:
                                    return {"error":  "Radiomics learner: Training method was not provided"}
                                if "use_gpu" in content["data"][model_name].keys() and content["data"][model_name]["use_gpu"] is not None:
                                    use_gpu = content["data"][model_name]["use_gpu"]
                                else:
                                    use_gpu = False
                                if "seed" in content["data"][model_name].keys() and content["data"][model_name]["seed"] is not None:
                                    seed = content["data"][model_name]["seed"]
                                else:
                                    return {"error":  "Radiomics learner: seed was not provided"}

                                # Serperate variable table for training sets (repetitive but double-checking)
                                var_table_train = rad_tables_training.loc[patients_train, :]

                                # Training the model
                                model = learner.train_xgboost_model(
                                    var_table_train, 
                                    outcome_table_binary_train, 
                                    var_importance_threshold, 
                                    optimal_threshold,
                                    method=method,
                                    use_gpu=use_gpu,
                                    optimization_metric=optimization_metric,
                                    seed=seed
                                )

                                # Saving the trained model using pickle
                                if "nameSave" in content["data"][model_name].keys() and content["data"][model_name]["nameSave"] is not None:
                                    name_save_model = content["data"][model_name]["nameSave"]
                                else:
                                    return {"error":  "Radiomics learner: Name to save model was not provided"}
                                model_id = name_save_model + '_' + "var1"
                                path_model = os.path.dirname(path_results) + '/' + (model_id + '.pickle')
                                model_dict = MEDimage.learning.ml_utils.save_model(model, "None", path_model)

                                # --> C. Testing phase        
                                # C.1. Testing the XGBoost model and computing model response
                                response_train, response_test = learner.test_xgb_model(
                                    model,
                                    rad_tables_testing,
                                    [patients_train, patients_test]
                                ) 
                                if holdout_test:
                                    # --> D. Holdoutset testing phase
                                    # D.1. Prepare holdout test data
                                    # Loading and pre-processing
                                    rad_tables_holdout = list()
                                    for item in rad_var_struct['path'].values():
                                        # Reading the table
                                        path_radiomics_csv = item['csv']
                                        path_radiomics_txt = item['txt']
                                        image_type = item['type']
                                        rad_table_holdout = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patients_holdout)
                                        rad_tables_holdout.append(rad_table_holdout)
                                    
                                    # Combine the tables
                                    var_table_all_holdout = MEDimage.learning.ml_utils.combine_rad_tables(rad_tables_holdout)
                                    var_table_all_holdout.Properties['userData']['flags_processing'] = {}

                                    # D.2. Testing the XGBoost model and computing model response on the holdout set
                                    response_holdout = learner.test_xgb_model(model, var_table_all_holdout, [patients_holdout])[0]
                                                
                                # E. Computing performance metrics
                                # Initialize the Results class
                                result = MEDimage.learning.Results(model_dict, model_id)
                                if holdout_test:
                                    run_results = result.to_json(
                                        response_train=response_train, 
                                        response_test=response_test,
                                        response_holdout=response_holdout, 
                                        patients_train=patients_train, 
                                        patients_test=patients_test, 
                                        patients_holdout=patients_holdout
                                    )
                                else:
                                    run_results = result.to_json(
                                        response_train=response_train, 
                                        response_test=response_test,
                                        response_holdout=None, 
                                        patients_train=patients_train, 
                                        patients_test=patients_test, 
                                        patients_holdout=None
                                    )
                                
                                # Calculating performance metrics for training phase and saving the ROC curve
                                run_results[model_id]['train']['metrics'] = result.get_model_performance(
                                    response_train,
                                    outcome_table_binary_train
                                )
                                
                                # Calculating performance metrics for testing phase and saving the ROC curve
                                run_results[model_id]['test']['metrics'] = result.get_model_performance(
                                    response_test,
                                    outcome_table_binary_test
                                )

                                if holdout_test:
                                    # Calculating performance metrics for holdout phase and saving the ROC curve
                                    run_results[model_id]['holdout']['metrics'] = result.get_model_performance(
                                        response_holdout, 
                                        outcome_table_binary_holdout
                                    )

                                # F. Saving the results dictionary
                                MEDimage.utils.json_utils.save_json(path_results, run_results, cls=NumpyEncoder)
                                saved_results = True
                                self.set_progress(now=round((split_counter+1) * (90 / len(paths_splits)) + 10))

                                # Increment the split counter
                                split_counter += 1

                            except Exception as e:
                                return {"error": str(e)}

                    # add relevant nodes
                    if (update_pip):
                        pip_obj[content["id"]] = id_obj

                        # Break the loop
                        break

                if saved_results and split_counter == len(paths_splits):
                    try:
                        # Average results of the different splits/runs
                        MEDimage.learning.ml_utils.average_results(Path(path_study) / f'learn__{experiment_label}', save=True)

                        # Analyze the features importance for all the runs
                        MEDimage.learning.ml_utils.feature_imporance_analysis(Path(path_study) / f'learn__{experiment_label}')

                        # Find analyze node after all splits are done
                        for node in pip:
                            analysis_dict = {}
                            # --------------------------- ANALYSIS ---------------------------
                            if content["name"].lower() == "analyze":
                                # Initializing options
                                if "histogram" in content["data"].keys() and content["data"]["histogram"]:
                                    if "histParams" not in content["data"].keys() or content["data"]["histParams"] is None:
                                        return {"error":  "Analyze: Histogram parameters were not provided"}
                                    if "sortOption" not in content["data"]["histParams"].keys() or content["data"]["histParams"]["sortOption"] is None:
                                        return {"error":  "Analyze: Sort option was not provided"}
                                    
                                    # Plot histogram
                                    try:
                                        result.plot_features_importance_histogram(
                                            Path(path_study), 
                                            experiment=experiment_label.split("_")[0], 
                                            level=experiment_label.split("_")[1], 
                                            modalities=[experiment_label.split("_")[-1]],
                                            sort_option=content["data"]["histParams"]["sortOption"],
                                            figsize=(20, 20),
                                            save=True
                                        )
                                    except Exception as e:
                                        return {"error": str(e)}
                                    
                                    # Move images to public folder
                                    level = experiment_label.split("_")[1]
                                    modality = experiment_label.split("_")[-1]
                                    sort_option = content["data"]["histParams"]["sortOption"]
                                    path_image = Path(path_study) / f'features_importance_histogram_{level}_{modality}_{sort_option}.png'
                                    path_save = Path.cwd().parent / "renderer/public/images/analyze" / f'features_importance_histogram_{level}_{modality}_{sort_option}_{pip_name}.png'
                                    path_save = shutil.copy(path_image, path_save)

                                    # Update Analysis dict
                                    analysis_dict = {}
                                    analysis_dict[experiment_label] = {}
                                    analysis_dict[experiment_label]["histogram"] = {}
                                    analysis_dict[experiment_label]["histogram"]["path"] = '.' + str(path_save).split('public')[-1].replace('\\', '/')

                                # Break the loop
                                break

                        # Update results dict
                        results_avg_dict = MEDimage.utils.load_json(Path(path_study) / f'learn__{experiment_label}' / 'results_avg.json')
                        
                        # Add experiment label to results, analysis results and round all the values
                        if "train" in results_avg_dict.keys() and results_avg_dict["train"] != {}:
                            results_avg_dict["train"] = self.__round_dict(results_avg_dict["train"], 2)
                        if "test" in results_avg_dict.keys() and results_avg_dict["test"] != {}:
                            results_avg_dict["test"] = self.__round_dict(results_avg_dict["test"], 2)
                        if "holdout" in results_avg_dict.keys() and results_avg_dict["holdout"] != {}:
                            results_avg_dict["holdout"] = self.__round_dict(results_avg_dict["holdout"], 2)
                        results_avg.append({pip_name: {experiment_label: results_avg_dict, "analysis": analysis_dict}})

                    except Exception as e:
                        return {"error": "Reults averaging & Features analysis:" + str(e)}
                
                # Check if all the splits are done
                if designed_experiment and split_counter == len(paths_splits):
                    break

        # Update progress
        self.set_progress(now=100, label="Done!")

        # After all pips are executed, analyze both
        # Find pips linked to analyze nodes
        experiments_labels = []
        for pip in pips:
            have_analyze = True
            for node in pip:
                content = get_node_content(node, json_scene)
                if content["name"].lower() == "analyze":
                    have_analyze = True
                    break
            for node in pip:
                content = get_node_content(node, json_scene)
                if content["name"].lower() == "design" and have_analyze and content["data"]["expName"] not in experiments_labels:
                    experiments_labels.append(content["data"]["expName"])
                    break
        
        # Check
        experiment = experiments_labels[0].split("_")[0]
        for exp_label in experiments_labels:
            if exp_label.split("_")[0] != experiment:
                return {"error": f"To analyze experiments, labels must start with the same name! {experiment} != {exp_label}"}
            
        # Analyze all pips linked to analyze nodes
        figures_dict = {}
        for pip in pips:
            for node in pip:
                content = get_node_content(node, json_scene)
                if content["name"].lower() == "analyze":
                    # --------------------------- ANALYSIS ---------------------------
                    # Initializing options
                    if "heatmap" in content["data"].keys() and content["data"]["heatmap"]:
                        if "heatmapParams" not in content["data"].keys() or content["data"]["heatmapParams"] is None:
                            return {"error":  "Analyze: Heatmap parameters were not provided"}
                        if "metric" not in content["data"]["heatmapParams"].keys() or content["data"]["heatmapParams"]["metric"] is None:
                            return {"error":  "Analyze: Heatmap metric was not provided"}
                        if "pValues" not in content["data"]["heatmapParams"].keys() or content["data"]["heatmapParams"]["pValues"] is None:
                            return {"error":  "Analyze: Heatmap p-values option was not provided"}
                        if "pValuesMethod" not in content["data"]["heatmapParams"].keys() or content["data"]["heatmapParams"]["pValuesMethod"] is None:
                            return {"error":  "Analyze: Heatmap p-value method was not provided"}
                        
                        # If no errors, retrieve the heatmap parameters
                        metric = content["data"]["heatmapParams"]["metric"]
                        plot_p_values = content["data"]["heatmapParams"]["pValues"]
                        p_value_test = content["data"]["heatmapParams"]["pValuesMethod"]

                        # Other params
                        if "title" in content["data"]["heatmapParams"].keys() and content["data"]["heatmapParams"]["title"] is not None:
                            title = content["data"]["heatmapParams"]["title"]
                        else:
                            title = None
                        if "extraMetrics" in content["data"]["heatmapParams"].keys() and content["data"]["heatmapParams"]["extraMetrics"] is not None:
                            stat_extra = content["data"]["heatmapParams"]["extraMetrics"].split(',')
                        else:
                            stat_extra = None

                        # Plot histogram
                        try:
                            result.plot_heatmap(
                                Path(path_study), 
                                experiment=experiment, 
                                levels=[exp_label.split("_")[1] for exp_label in experiments_labels],
                                modalities=list(set([exp_label.split("_")[-1] for exp_label in experiments_labels])),
                                metric=metric,
                                stat_extra=stat_extra,
                                title=title,
                                plot_p_values=plot_p_values,
                                p_value_test=p_value_test,
                                save=True)
                        except Exception as e:
                            return {"error": str(e)}
                        
                        # Move images to public folder
                        path_image = Path(path_study) / f'{title}.png' if title else Path(path_study) / f'{metric}_heatmap.png'
                        path_save = Path.cwd().parent / "renderer/public/images/analyze" / f'{title}_{pip_name}.png' if title else Path.cwd().parent / "renderer/public/images/analyze" / f'{metric}_heatmap_{pip_name}.png'
                        path_save = shutil.copy(path_image, path_save)

                        # Update results dict with new figures
                        figures_dict["heatmap"] = {}
                        figures_dict["heatmap"]["path"] = '.' + str(path_save).split('public')[-1].replace('\\', '/')

                    # Find optimal level
                    if "optimalLevel" in content["data"].keys() and content["data"]["optimalLevel"] is not None:
                        find_optimal_level = content["data"]["optimalLevel"]
                    else:
                        find_optimal_level = False
                    if "tree" in content["data"].keys() and content["data"]["tree"] is not None:
                        plot_tree = content["data"]["tree"]
                    else:
                        plot_tree = False
                    if find_optimal_level:
                        try:
                            optimal_levels = result.get_optimal_level(
                                Path(path_study), 
                                experiment=experiment, 
                                levels=list(set([exp_label.split("_")[1] for exp_label in experiments_labels])),
                                modalities=list(set([exp_label.split("_")[-1] for exp_label in experiments_labels])),
                                metric=metric,
                                p_value_test=p_value_test,
                                )
                        except Exception as e:
                            return {"error": str(e)}
                    
                        # Update Analysis dict
                        figures_dict["optimal_level"] = {}
                        figures_dict["optimal_level"]["name"] = optimal_levels

                        # Extra optimal level analysis
                        if plot_tree:
                            try:
                                modalities = list(set([exp_label.split("_")[-1] for exp_label in experiments_labels]))
                                for idx_m, optimal_level in enumerate(optimal_levels):
                                    path_tree = None
                                    if "Text" in optimal_level:
                                        # Plot tree
                                        result.plot_original_level_tree(
                                            Path(path_study), 
                                            experiment=experiment,
                                            level=optimal_level,
                                            modalities=[modalities[idx_m]] if len(modalities) == 1 else modalities[idx_m],
                                            figsize=(25, 10),
                                        )
                                        # Get image path
                                        path_tree = Path(path_study) / f'Original_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation_tree.png'
                                        
                                    elif "LF" in optimal_level:
                                        result.plot_lf_level_tree(
                                            Path(path_study), 
                                            experiment=experiment,
                                            level=optimal_level,
                                            modalities=[modalities[idx_m]] if len(modalities) == 1 else modalities[idx_m],
                                            figsize=(25, 10),
                                        )
                                        # Get image path
                                        path_tree = Path(path_study) / f'LF_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation_tree.png'
                                    
                                    elif "TF" in optimal_level:
                                        result.plot_tf_level_tree(
                                            Path(path_study), 
                                            experiment=experiment,
                                            level=optimal_level,
                                            modalities=[modalities[idx_m]] if len(modalities) == 1 else modalities[idx_m],
                                            figsize=(25, 10),
                                        )
                                        # Get image path
                                        path_tree = Path(path_study) / f'TF_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation_tree.png'
                                    
                                    # Move plot to public folder
                                    if path_tree is not None:
                                        if 'Text' in optimal_level:
                                            path_save = Path.cwd().parent / "renderer/public/images/analyze" / f'Original_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation_tree_{pip_name}.png'
                                        elif 'LF' in optimal_level:
                                            path_save = Path.cwd().parent / "renderer/public/images/analyze" / f'LF_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation_tree_{pip_name}.png'
                                        elif 'TF' in optimal_level:
                                            path_save = Path.cwd().parent / "renderer/public/images/analyze" / f'TF_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation_tree_{pip_name}.png'
                                        path_save = shutil.copy(path_tree, path_save)

                                        # Update Analysis dict
                                        figures_dict["optimal_level"]["tree"] = {}
                                        figures_dict["optimal_level"]["tree"][optimal_level] = {}
                                        figures_dict["optimal_level"]["tree"][optimal_level]["path"] = '.' + str(path_save).split('public')[-1].replace('\\', '/')
                            except Exception as e:
                                return {"error": str(e)}
                    
                    # Break the nodes loop
                    break

            # Break the pips loop (only one analyze node is allowed per scence)
            break
        
        # pip features and settings updateded
        scan_res[pip_name_res] = pip_res
    
        # pips response update
        pips_res[filename_loaded] = scan_res
        pips_res["experiments"] = experiments_labels
        pips_res["results_avg"] = results_avg
        pips_res["figures"] = figures_dict
        pips_res["pips"] = pips

        # pips object update
        pips_obj[pip_name_obj] = pip_obj  

        return pips_res

    def run_all(self):
        # Retrieve the json scene from frontend
        json_scene = self.json_config
        drawflow_scene = json_scene['drawflow']

        # Initialize pipeline list
        pips = []
        counter = 0

        # Check if every design node has a split node as input
        for module in drawflow_scene:
            for node_id in drawflow_scene[module]['data']:
                node_content = drawflow_scene[module]['data'][node_id]
                if node_content["name"].lower() == "design":
                    if len(node_content["inputs"]) == 0:
                        return {"error": "Every design node must have a split node as input!"}

        # Check if there is more than one analyze node
        analyze_nodes = 0
        for module in drawflow_scene:
            for node_id in drawflow_scene[module]['data']:
                node_content = drawflow_scene[module]['data'][node_id]
                if node_content["name"].lower() == "analyze":
                    analyze_nodes += 1
                if analyze_nodes > 1:
                    return {"error": "Only one analyze node is allowed!"}
        
        # Process Piplines starting with split
        for module in drawflow_scene:  # We scan all module in scene
            for node_id in drawflow_scene[module]['data']:  # We scan all node of each module in scene
                node_content = drawflow_scene[module]['data'][node_id]  # Getting node content
                if len(node_content["inputs"]) == 0:
                    self.generate_all_pips(str(node_content["id"]), node_content, [], json_scene, pips, counter)
                    counter += 1
        
        # Full expeience check
        design_nodes = 0
        for module in drawflow_scene:
            for node_id in drawflow_scene[module]['data']:
                node_content = drawflow_scene[module]['data'][node_id]
                if node_content["name"].lower() == "design":
                    design_nodes += 1

        # Full experiment check
        warn_msg = ""
        if design_nodes != len(pips):
            warn_msg =  f"{str(len(pips))} detected pipelines, but only {str(design_nodes)} design nodes were found! This may cause errors!"

        print("\n The pipelines found in the current drawflow scene are : ", pips)
        json_res = self.execute_pips(pips, json_scene)

        if warn_msg:
            json_res["warning"] = warn_msg

        return json_res  # return pipeline results in the form of a dict
    
    def generate_notebooks(self) -> dict:
        """
        This function is called by the frontend to generate the Jupyter notebooks for the pipelines.\n

        Returns:
            dict: The response containing the status of the notebook generation.
        """
        # Safety checks
        pips = self.json_config["pips"]
        if len(pips) == 0:
            return {"error": "No pipeline to generate!"}

        # Retrieve the path to save the results
        for idx, pip in enumerate(pips):
            for node in pip:
                content = [x for x in self.json_config["nodes"] if x["id"] == node][0]
                if content["name"].lower() == "split":
                    path_save_experiments = Path(content['data']['path_save_experiments'])
                    outcome_name = content["data"]["outcome_name"]
                    break

        # Create a python file
        f = open(path_save_experiments / f'temp_notebook_code.py', 'w')

        # Disclaimer
        f.writelines("# # This notebook is auto-generated from the selected pipeline made with the interface\n")

        # Add date
        f.writelines("\n# **Date of creation: " + str(datetime.now()) + "**\n")

        # Add imports
        f.writelines("\n# Imports\n")
        f.writelines("import json\n")
        f.writelines("import os\n")
        f.writelines("import pandas as pd\n")
        f.writelines("from copy import deepcopy\n")
        f.writelines("from pathlib import Path\n")
        f.writelines("\nfrom numpyencoder import NumpyEncoder\n")
        f.writelines("import MEDimage\n")
        
        # ------------------------------------------ PIP EXECUTION ------------------------------------------
        piplines_all = []
        for idx, pip in enumerate(pips):

            pip_name = "pipeline" + str(idx+1)

            # Get experiment name
            for node in pip:
                content = [x for x in self.json_config["nodes"] if x["id"] == node][0]
                if content["name"].lower() == "design":
                    exp_name = content["data"]["expName"]
                    break
            
            # List of experiments
            f.writelines(f"\n# Experiment: {exp_name}\n")

            # Init object and variables for new pipeline
            pip_name_obj = ""
            pip_name_res = "pip"
            splitted_data = False
            cleaned_data = False
            normalized_features = False
            reduced_features = False
            designed_experiment = False
            loaded_data = False
            saved_results = False
            
            # ------------------------------------------ NODE EXECUTION ------------------------------------------
            for node in pip:
                # Get node content
                content = [x for x in self.json_config["nodes"] if x["id"] == node][0]

                # Update RUNS dict for store instances and logs (xxx_obj)
                pip_name_obj += node

                # Update results dict for result response (xxx_res)
                pip_name_res += "/" + node

                # ------------------------------------------ HOME ------------------------------------------
                # Split
                if (content["name"].lower() == "split"):
                    f.writelines("\n# **1. Data Splitting**\n")
                    f.writelines("\n# Settings:\n")
                    f.writelines(f"split_settings = {pp.pformat(content['data'])}\n")
                    if not splitted_data:
                        f.writelines("\n# Retrieving data from json request\n")
                        f.writelines("path_outcome_file = Path(split_settings['path_outcome_file'])\n")
                        f.writelines("path_save_experiments = Path(split_settings['path_save_experiments'])\n")
                        f.writelines("outcome_name = split_settings['outcome_name']\n")
                        f.writelines("method = split_settings['method']\n")
                        f.writelines("if method == 'all_learn':\n")
                        f.writelines("    holdout_test = False\n")
                        f.writelines("else:\n")
                        f.writelines("    holdout_test = True\n")
                        f.writelines("\n# Generate the machine learning experiment\n")
                        f.writelines("path_study, _ = MEDimage.learning.ml_utils.create_holdout_set(\n")
                        f.writelines("    path_outcome_file=path_outcome_file,\n")
                        f.writelines("    path_save_experiments=path_save_experiments,\n")
                        f.writelines("    outcome_name=outcome_name,\n")
                        f.writelines("    method=method\n")
                        f.writelines(")\n")

                # Design
                if (content["name"].lower() == "design"):
                    if not designed_experiment:
                        f.writelines("\n# **2. Designing the experiment**\n")
                        f.writelines("\n# Settings:\n")
                        f.writelines(f"design_settings = {pp.pformat(content['data'])}\n")

                        f.writelines("\n# Initialize the DesignExperiment class\n")
                        f.writelines("path_settings = Path.cwd() / 'flask_server' / 'learning_MEDimage' / 'settings'\n")
                        f.writelines("experiment = MEDimage.learning.DesignExperiment(path_study, path_settings, design_settings['expName'])\n")

                        f.writelines("\n# Generate the machine learning experiment\n")
                        f.writelines("design_settings['design'] = design_settings\n")
                        f.writelines("tests_dict = experiment.create_experiment(design_settings)\n")

                        f.writelines("\n# Initializing experiment data\n")
                        f.writelines("experiment_label = design_settings['expName']\n")
                        f.writelines("paths_splits = [tests_dict[run] for run in tests_dict.keys()]\n")
                        f.writelines("\n# Numebr of splits\n")
                        f.writelines("nb_split = len(paths_splits)\n")

                        f.writelines("# make sure we have at least two splits\n")
                        f.writelines("assert nb_split > 1, 'Number of splits must be at least 2!'\n")

                        f.writelines("\n# **3. Data Loading, Model training and testing**\n") 

                        f.writelines("\n# **This is where all the magic happens (Main ML function)**\n")

                        f.writelines("\ndef ml_learn(path_ml):\n")

                        # Update
                        designed_experiment = True

                # Model training/testing part
                if designed_experiment:            
                    # Data
                    if (content["name"].lower() == "data"):                 
                        f.writelines("\n    # A. Initialization phase\n")

                        f.writelines("\n    # Load the test dictionary and machine learning information\n")
                        f.writelines("    ml_dict_paths = MEDimage.utils.load_json(path_ml)\n")

                        f.writelines("\n    # Machine learning information dictionary\n")
                        f.writelines("    ml_info_dict = dict()\n")

                        f.writelines("\n    # Training and test patients\n")
                        f.writelines("    ml_info_dict['patientsTrain'] = MEDimage.utils.load_json(ml_dict_paths['patientsTrain'])\n")
                        f.writelines("    ml_info_dict['patientsTest'] = MEDimage.utils.load_json(ml_dict_paths['patientsTest'])\n")

                        f.writelines("\n    # Outcome table for training and test patients\n")
                        f.writelines("    outcome_table = pd.read_csv(ml_dict_paths['outcomes'], index_col=0)\n")
                        f.writelines("    ml_info_dict['outcome_table_binary'] = outcome_table.iloc[:, [0]]\n")
                        f.writelines("    if outcome_table.shape[1] == 2:\n")
                        f.writelines("        ml_info_dict['outcome_table_time'] = outcome_table.iloc[:, [1]]\n")
                        
                        f.writelines("\n    # Machine learning dictionary\n")
                        f.writelines("    ml_info_dict['path_results'] = ml_dict_paths['results']\n")

                        f.writelines("\n    # Machine learning assets\n")
                        f.writelines("    patients_train = ml_info_dict['patientsTrain']\n")
                        f.writelines("    patients_test = ml_info_dict['patientsTest']\n")
                        f.writelines("    patients_holdout = MEDimage.utils.load_json(path_study / 'patientsHoldOut.json') if holdout_test else None\n")
                        f.writelines("    outcome_table_binary = ml_info_dict['outcome_table_binary']\n")
                        f.writelines("    path_results = ml_info_dict['path_results']\n")
                        f.writelines("    patient_ids = list(outcome_table_binary.index)\n")
                        f.writelines("    outcome_table_binary_training = outcome_table_binary.loc[patients_train]\n")
                        f.writelines("    flags_preprocessing = []\n")
                        f.writelines("    flags_preprocessing_test = []\n")
                        f.writelines("    rad_tables_learning = list()\n")

                        f.writelines("\n    # --> B. Pre-processing phase\n")
                        f.writelines("\n    # B.1. Pre-processing initialization, settings tables paths\n")
                        f.writelines("\n    # Settings:\n")
                        f.writelines(f"    data_settings = {pp.pformat(content['data'])}\n")
                        f.writelines("    rad_var_struct = dict()\n")

                        f.writelines("\n    # For each variable, organize the option in the ML dictionary\n")
                        f.writelines("    if 'nameType' in data_settings.keys() and data_settings['nameType'] != '':\n")
                        f.writelines("        name_type = data_settings['nameType']\n")
                        f.writelines("    else:\n")
                        f.writelines("        name_type = 'radiomics'\n")
                        f.writelines("\n    # Radiomics variables\n")
                        f.writelines("    if 'radiomics' not in name_type.lower():\n")
                        f.writelines("        raise TypeError('Data node: Only Radiomics variables are supported!')\n")
                        
                        f.writelines("\n    # Get radiomics features folder\n")
                        f.writelines("    path_features = Path(data_settings['path'])\n")
                        f.writelines("    features_files = data_settings['featuresFiles']\n")
                        f.writelines("    for file in features_files:\n")
                        f.writelines("        if not file.endswith('.csv'):\n")
                        f.writelines("            raise TypeError('Data node: Only csv files are supported!')\n")

                            
                        f.writelines("\n    # Initialize dict to hold all paths to radiomics features (csv and txt files)\n")
                        f.writelines("    path = dict()\n")
                        f.writelines("    for idx, feature_file in enumerate(features_files):\n")
                        f.writelines("        rad_tab_x = dict()\n")
                        f.writelines("        name_tab = 'radTab' + str(idx+1)\n")
                        f.writelines("        rad_tab_x['csv'] = Path(path_features / feature_file)\n")
                        f.writelines("        rad_tab_x['txt'] = Path(path_features / (feature_file.split('.')[0] + '.txt'))\n")
                        f.writelines("        rad_tab_x['type'] = feature_file.split('__')[1].split('_')[0] if '__' in feature_file else 'None'\n")

                        f.writelines("\n        # check if file exist\n")
                        f.writelines("        if not rad_tab_x['csv'].exists():\n")
                        f.writelines("            raise FileNotFoundError(f\"File {rad_tab_x['csv']} does not exist.\")\n")
                        f.writelines("        if not rad_tab_x['txt'].exists():\n")
                        f.writelines("            raise FileNotFoundError(f\"File {rad_tab_x['txt']} does not exist.\")\n")
                            
                        f.writelines("\n        path[name_tab] = rad_tab_x\n")
                            
                        f.writelines("        # Add path to ml dict for the current variable\n")
                        f.writelines("        rad_var_struct['path'] = path\n")

                        # Update
                        loaded_data = True

                    # Cleaning
                    if (content["name"].lower() == "cleaning"):
                        f.writelines("\n    # Data cleaning\n")
                        f.writelines("\n    # Settings\n")
                        f.writelines(f"    cleaning_settings = {pp.pformat(content['data'])}\n")

                        f.writelines("\n    # Pre-processing\n")
                        f.writelines("    for item in rad_var_struct['path'].values():\n")
                        f.writelines("        # Loading the table\n")
                        f.writelines("        path_radiomics_csv = item['csv']\n")
                        f.writelines("        path_radiomics_txt = item['txt']\n")
                        f.writelines("        image_type = item['type']\n")
                        f.writelines("        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)\n")

                        f.writelines("        # Avoid future bugs (caused in Windows)\n")
                        f.writelines("        if type(rad_table_learning.Properties['Description']) not in [str, Path]:\n")
                        f.writelines("            rad_table_learning.Properties['Description'] = str(rad_table_learning.Properties['Description'])\n")

                        f.writelines("        # Data cleaning\n")
                        f.writelines("        data_cln_method = list(cleaning_settings.keys())[0]\n")
                        f.writelines("        cleaning_dict = cleaning_settings[data_cln_method]['feature']['continuous']\n")
                        f.writelines("        data_cleaner = MEDimage.learning.DataCleaner(rad_table_learning)\n")
                        f.writelines("        rad_table_learning = data_cleaner(cleaning_dict)\n")
                        f.writelines("        if rad_table_learning is None:\n")
                        f.writelines("            continue\n")
                        f.writelines("        rad_tables_learning.append(rad_table_learning)\n")
                        
                        f.writelines("\n    # Finalization steps\n")
                        f.writelines("    flags_preprocessing.append('var_datacleaning')\n")
                        f.writelines("    flags_preprocessing_test.append('var_datacleaning')\n")

                        cleaned_data = True
                    
                    if (content["name"].lower() == "normalization"):
                        f.writelines("\n    # Features normalization\n")
                        f.writelines("\n    # Settings\n")
                        f.writelines(f"    normalization_settings = {pp.pformat(content['data'])}\n")
                        f.writelines("    normalization_method = normalization_settings['method']\n")

                        # If there was no cleaning step, the data must be loaded
                        if not cleaned_data:
                            f.writelines("    for item in rad_var_struct['path'].values():\n")
                            f.writelines("        # Loading the table\n")
                            f.writelines("        path_radiomics_csv = item['csv']\n")
                            f.writelines("        path_radiomics_txt = item['txt']\n")
                            f.writelines("        image_type = item['type']\n")
                            f.writelines("        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)\n")
                            f.writelines("        rad_tables_learning.append(rad_table_learning)\n")

                        f.writelines("\n    # Start features normalization for each table\n")
                        f.writelines("    for rad_table_learning in rad_tables_learning:\n")
                        f.writelines("        # Some information must be stored to re-apply combat for testing data\n")
                        f.writelines("        if 'combat' in normalization_method.lower():\n")
                        f.writelines("            # Training data\n")
                        f.writelines("            rad_table_learning.Properties['userData']['normalization'] = dict()\n")
                        f.writelines("            rad_table_learning.Properties['userData']['normalization']['original_data'] = dict()\n")
                        f.writelines("            rad_table_learning.Properties['userData']['normalization']['original_data']['path_radiomics_csv'] = str(path_radiomics_csv)\n")
                        f.writelines("            rad_table_learning.Properties['userData']['normalization']['original_data']['path_radiomics_txt'] = str(path_radiomics_txt)\n")
                        f.writelines("            rad_table_learning.Properties['userData']['normalization']['original_data']['image_type'] = str(image_type)\n")
                        f.writelines("            rad_table_learning.Properties['userData']['normalization']['original_data']['patient_ids'] = patient_ids\n")
                        if cleaned_data:
                            f.writelines("            data_cln_method = data_cln_method\n")
                            f.writelines("            rad_table_learning.Properties['userData']['normalization']['original_data']['datacleaning_method'] = data_cln_method\n")
                                
                        f.writelines("            # Apply ComBat\n")
                        f.writelines("            normalization = MEDimage.learning.Normalization('combat')\n")
                        f.writelines("            rad_table_learning = normalization.apply_combat(variable_table=rad_table_learning)\n")
                            
                        normalized_features = True

                    if (content["name"].lower() == "feature reduction"):
                        # Load data if cleaning step or normalization step was not performed
                        f.writelines("\n    # Feature set reduction\n")
                        f.writelines("\n    # Settings\n")
                        f.writelines(f"    fsr_settings = {pp.pformat(content['data'])}\n")
                        if not cleaned_data and not normalized_features:
                            f.writelines("    for item in rad_var_struct['path'].values():\n")
                            f.writelines("        # Loading the tablen\n")
                            f.writelines("        path_radiomics_csv = item['csv']\n")
                            f.writelines("        path_radiomics_txt = item['txt']\n")
                            f.writelines("        image_type = item['type']\n")
                            f.writelines("        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)\n")
                            f.writelines("        rad_tables_learning.append(rad_table_learning)\n")

                        f.writelines("\n    # Seperate training and testing data before feature set reduction\n")
                        f.writelines("    rad_tables_testing = deepcopy(rad_tables_learning)\n")
                        f.writelines("    rad_tables_training = []\n")
                        f.writelines("    for rad_tab in rad_tables_learning:\n")
                        f.writelines("        patients_ids = MEDimage.learning.ml_utils.intersect(patients_train, list(rad_tab.index))\n")
                        f.writelines("        rad_tables_training.append(deepcopy(rad_tab.loc[patients_ids]))\n")

                        f.writelines("\n    # Deepcopy properties\n")
                        f.writelines("    temp_properties = list()\n")
                        f.writelines("    for rad_tab in rad_tables_testing:\n")
                        f.writelines("        temp_properties.append(deepcopy(rad_tab.Properties))\n")
                        
                        f.writelines("\n    # Feature set reduction method\n")
                        f.writelines("    f_set_reduction_method = fsr_settings['method']\n")
                        
                        f.writelines("\n    # Prepare FDA settings dict\n")
                        f.writelines("    fsr_dict = dict()\n")
                        f.writelines("    fsr_dict['fSetReduction'] = dict()\n")
                        f.writelines("    fsr_dict['fSetReduction']['FDA'] = fsr_settings['FDA']\n")

                        f.writelines("\n    # Initialize the FSR class\n")
                        f.writelines("    fsr = MEDimage.learning.FSR(f_set_reduction_method)\n")
                        
                        f.writelines("\n    # Apply FDA\n")
                        f.writelines("    rad_tables_training = fsr.apply_fsr(\n")
                        f.writelines("        fsr_dict, \n")
                        f.writelines("        rad_tables_training, \n")
                        f.writelines("        outcome_table_binary_training, \n")
                        f.writelines("        path_save_logging=path_results\n")
                        f.writelines("    )\n")
                    
                        f.writelines("\n    # Finalize processing tables\n")
                        f.writelines("\n    # Re-assign properties\n")
                        f.writelines("    for i in range(len(rad_tables_testing)):\n")
                        f.writelines("        rad_tables_testing[i].Properties = temp_properties[i]\n")
                        f.writelines("    del temp_properties\n")

                        f.writelines("\n    # Finalization steps\n")
                        f.writelines("    rad_tables_training.Properties['userData']['flags_preprocessing'] = flags_preprocessing\n")
                        f.writelines("    rad_tables_testing = MEDimage.learning.ml_utils.combine_rad_tables(rad_tables_testing)\n")
                        f.writelines("    rad_tables_testing.Properties['userData']['flags_processing'] = flags_preprocessing_test\n")
                
                        reduced_features = True

                    # --------------------------- MODEL TRAINING ---------------------------
                    if content["name"].lower() == "radiomics learner":
                        # If no cleaning, normalization or feature set reduction step was performed, the data must be loaded
                        f.writelines("\n    # Radiomics learner\n")
                        f.writelines("\n    # Settings\n")
                        f.writelines(f"    learner_settings = {pp.pformat(content['data'])}\n")
                        if not loaded_data:
                            return {"error":  "Cleaning: Data must be loaded first! Use Data node."}
                        if not cleaned_data and not normalized_features and not reduced_features:
                            f.writelines("    for item in rad_var_struct['path'].values():\n")
                            f.writelines("        # Loading the table\n")
                            f.writelines("        path_radiomics_csv = item['csv']\n")
                            f.writelines("        path_radiomics_txt = item['txt']\n")
                            f.writelines("        image_type = item['type']\n")
                            f.writelines("        rad_table_learning = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)\n")
                            f.writelines("        rad_tables_learning.append(rad_table_learning)\n")
                        
                        f.writelines("\n    # Seperate training and testing if no feature set reduction step was performed\n")
                        if not reduced_features:
                            f.writelines("        rad_tables_testing = deepcopy(rad_tables_learning)\n")
                            f.writelines("        rad_tables_training = []\n")
                            f.writelines("        for rad_tab in rad_tables_learning:\n")
                            f.writelines("            patients_ids = MEDimage.learning.ml_utils.intersect(patients_train, list(rad_tab.index))\n")
                            f.writelines("            rad_tables_training.append(deepcopy(rad_tab.loc[patients_ids]))\n")
                        
                        f.writelines("\n    # B.2. Pre-learning initialization\n")
                        f.writelines("\n    # Patient definitions (training and test sets)\n")
                        f.writelines("    patient_ids = list(outcome_table_binary.index)\n")
                        f.writelines("    patients_train = MEDimage.learning.ml_utils.intersect(MEDimage.learning.ml_utils.intersect(patient_ids, patients_train), rad_tables_training.index)\n")
                        f.writelines("    patients_test = MEDimage.learning.ml_utils.intersect(MEDimage.learning.ml_utils.intersect(patient_ids, patients_test), rad_tables_testing.index)\n")
                        f.writelines("    patients_holdout = MEDimage.learning.ml_utils.intersect(patient_ids, patients_holdout) if holdout_test else None\n")

                        f.writelines("\n    # Initializing outcome tables for training and test sets\n")
                        f.writelines("    outcome_table_binary_train = outcome_table_binary.loc[patients_train, :]\n")
                        f.writelines("    outcome_table_binary_test = outcome_table_binary.loc[patients_test, :]\n")
                        f.writelines("    outcome_table_binary_holdout = outcome_table_binary.loc[patients_holdout, :] if holdout_test else None\n")

                        f.writelines("\n    # Initializing XGBoost model settings\n")
                        f.writelines("    model_name = learner_settings['model']\n")
                        f.writelines("    var_importance_threshold = learner_settings[model_name]['varImportanceThreshold']\n")
                        f.writelines("    optimal_threshold = learner_settings[model_name]['optimalThreshold']\n")
                        f.writelines("    optimization_metric = learner_settings[model_name]['optimizationMetric']\n")
                        f.writelines("    method = learner_settings[model_name]['method']\n")
                        f.writelines("    use_gpu = learner_settings[model_name]['use_gpu']  if 'use_gpu' in learner_settings[model_name] else False\n")
                        f.writelines("    seed = learner_settings[model_name]['seed']\n")

                        f.writelines("\n    # Serperate variable table for training sets (repetitive but double-checking)\n")
                        f.writelines("    var_table_train = rad_tables_training.loc[patients_train, :]\n")

                        f.writelines("\n    # Training the model\n")
                        f.writelines("    learner = MEDimage.learning.RadiomicsLearner(path_study=path_study, path_settings=Path.cwd(), experiment_label=experiment_label)\n")
                        f.writelines("    model = learner.train_xgboost_model(\n")
                        f.writelines("        var_table_train, \n")
                        f.writelines("        outcome_table_binary_train, \n")
                        f.writelines("        var_importance_threshold, \n")
                        f.writelines("        optimal_threshold,\n")
                        f.writelines("        method=method,\n")
                        f.writelines("        use_gpu=use_gpu,\n")
                        f.writelines("        optimization_metric=optimization_metric,\n")
                        f.writelines("        seed=seed\n")
                        f.writelines("    )\n")

                        f.writelines("\n    # Saving the trained model using pickle\n")
                        f.writelines("    name_save_model = learner_settings[model_name]['nameSave']\n")
                        f.writelines("    model_id = name_save_model + '_' + 'var1'\n")
                        f.writelines("    path_model = os.path.dirname(path_results) + '/' + (model_id + '.pickle')\n")
                        f.writelines("    model_dict = MEDimage.learning.ml_utils.save_model(model, 'None', path_model)\n")

                        f.writelines("\n    # --> C. Testing phase\n")
                        f.writelines("\n    # C.1. Testing the XGBoost model and computing model response\n")
                        f.writelines("    response_train, response_test = learner.test_xgb_model(\n")
                        f.writelines("        model,\n")
                        f.writelines("        rad_tables_testing,\n")
                        f.writelines("        [patients_train, patients_test]\n")
                        f.writelines("    )\n")
                        f.writelines("    if holdout_test:\n")
                        f.writelines("        # --> D. Holdoutset testing phase\n")
                        f.writelines("        # D.1. Prepare holdout test data\n")
                        f.writelines("        # Loading and pre-processing\n")
                        f.writelines("        rad_tables_holdout = list()\n")
                        f.writelines("        for item in rad_var_struct['path'].values():\n")
                        f.writelines("            # Reading the table\n")
                        f.writelines("            path_radiomics_csv = item['csv']\n")
                        f.writelines("            path_radiomics_txt = item['txt']\n")
                        f.writelines("            image_type = item['type']\n")
                        f.writelines("            rad_table_holdout = MEDimage.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patients_holdout)\n")
                        f.writelines("            rad_tables_holdout.append(rad_table_holdout)\n")
                            
                        f.writelines("        # Combine the tables\n")
                        f.writelines("        var_table_all_holdout = MEDimage.learning.ml_utils.combine_rad_tables(rad_tables_holdout)\n")
                        f.writelines("        var_table_all_holdout.Properties['userData']['flags_processing'] = dict()\n")

                        f.writelines("        # D.2. Testing the XGBoost model and computing model response on the holdout set\n")
                        f.writelines("        response_holdout = learner.test_xgb_model(model, var_table_all_holdout, [patients_holdout])[0]\n")
                                        
                        f.writelines("\n    # E. Computing performance metrics\n")
                        f.writelines("\n    # Initialize the Results class\n")
                        f.writelines("    result = MEDimage.learning.Results(model_dict, model_id)\n")
                        f.writelines("    if holdout_test:\n")
                        f.writelines("        run_results = result.to_json(\n")
                        f.writelines("            response_train=response_train, \n")
                        f.writelines("            response_test=response_test,\n")
                        f.writelines("            response_holdout=response_holdout, \n")
                        f.writelines("            patients_train=patients_train, \n")
                        f.writelines("            patients_test=patients_test, \n")
                        f.writelines("            patients_holdout=patients_holdout\n")
                        f.writelines("        )\n")
                        f.writelines("    else:\n")
                        f.writelines("        run_results = result.to_json(\n")
                        f.writelines("            response_train=response_train, \n")
                        f.writelines("            response_test=response_test,\n")
                        f.writelines("            response_holdout=None, \n")
                        f.writelines("            patients_train=patients_train, \n")
                        f.writelines("            patients_test=patients_test, \n")
                        f.writelines("            patients_holdout=None\n")
                        f.writelines("        )\n")
                        
                        f.writelines("\n    # Calculating performance metrics for training phase and saving the ROC curve\n")
                        f.writelines("    run_results[model_id]['train']['metrics'] = result.get_model_performance(\n")
                        f.writelines("        response_train,\n")
                        f.writelines("        outcome_table_binary_train\n")
                        f.writelines("    )\n")
                        
                        f.writelines("\n    # Calculating performance metrics for testing phase and saving the ROC curve\n")
                        f.writelines("    run_results[model_id]['test']['metrics'] = result.get_model_performance(\n")
                        f.writelines("        response_test,\n")
                        f.writelines("        outcome_table_binary_test\n")
                        f.writelines("    )\n")

                        f.writelines("    if holdout_test:\n")
                        f.writelines("        # Calculating performance metrics for holdout phase and saving the ROC curve\n")
                        f.writelines("        run_results[model_id]['holdout']['metrics'] = result.get_model_performance(\n")
                        f.writelines("            response_holdout, \n")
                        f.writelines("            outcome_table_binary_holdout\n")
                        f.writelines("        )\n")

                        f.writelines("\n    # F. Saving the results dictionary\n")
                        f.writelines("    MEDimage.utils.json_utils.save_json(path_results, run_results, cls=NumpyEncoder)\n")
                        f.writelines("    saved_results = True\n")

                        saved_results = True

            if saved_results:
                f.writelines("\n# **Running the experiment for each split**\n")
                f.writelines("\nfor path_ml in paths_splits:\n")
                f.writelines("    ml_learn(path_ml)\n")
                
                f.writelines("\n#**4. Results averaging and analysis**\n")
                f.writelines("\n# Averaging\n")

                f.writelines("\n# Average results of the different splits/runs\n")
                f.writelines("MEDimage.learning.ml_utils.average_results(Path(path_study) / f'learn__" + '{experiment_label}' + "', save=True)\n")

                f.writelines("\n# Analyze the features importance for all the runs\n")
                f.writelines("MEDimage.learning.ml_utils.feature_imporance_analysis(Path(path_study) / f'learn__" + '{experiment_label}' + "')\n")
            
                # Find analyze node after all splits are done
                for node in pip:
                    content = [x for x in self.json_config["nodes"] if x["id"] == node][0]
                    # --------------------------- ANALYSIS ---------------------------
                    if content["name"].lower() == "analyze":
                        f.writelines("\n# Analysis of the experiment\n")
                        f.writelines("\n# Retrieve experiment\n")
                        f.writelines("experiment = experiment_label.split('_')[0]\n")
                        f.writelines("# Instantiate the Results class\n")
                        f.writelines("result = MEDimage.learning.Results()\n")
                        f.writelines("\n# Settings\n")
                        f.writelines(f"analyze_settings = {pp.pformat(content['data'])}\n")
                        
                        if 'histogram' in content["data"].keys() and content["data"]['histogram']:
                            f.writelines("\n# **Feature's Importance Histogram**\n")
                            f.writelines("\nresult.plot_features_importance_histogram(\n")
                            f.writelines("    Path(path_study), \n")
                            f.writelines("    experiment=experiment_label.split('_')[0], \n")
                            f.writelines("    level=experiment_label.split('_')[1], \n")
                            f.writelines("    modalities=[experiment_label.split('_')[-1]],\n")
                            f.writelines("    sort_option=analyze_settings['histParams']['sortOption'],\n")
                            f.writelines("    figsize=(20, 20),\n")
                            f.writelines("    save=False\n")
                            f.writelines(")\n")
                        
                        break

            piplines_all.append(outcome_name + "_" + pip_name)

        # After all pips are executed, analyze both
        f.writelines("\n")
        f.writelines("\n# **All Experiments Analysis**\n")
        f.writelines("\n")
        
        # Find pips linked to analyze nodes
        experiments_labels = []
        for pip in pips:
            have_analyze = True
            for node in pip:
                content = [x for x in self.json_config["nodes"] if x["id"] == node][0]
                if content["name"].lower() == "analyze":
                    have_analyze = True
                    break
            for node in pip:
                content = [x for x in self.json_config["nodes"] if x["id"] == node][0]
                if content["name"].lower() == "design" and have_analyze and content["data"]["expName"] not in experiments_labels:
                    experiments_labels.append(content["data"]["expName"])
                    break
        
        f.writelines("experiments_labels = " + str(experiments_labels) + " # All experiments labels\n")
        
        # Check and get experiment main name
        experiment = experiments_labels[0].split("_")[0]
        for exp_label in experiments_labels:
            if exp_label.split("_")[0] != experiment:
                return {"error": f"To analyze experiments, labels must start with the same name! {experiment} != {exp_label}"}
        f.writelines("experiment = '" + experiment + "' # Experiment name\n")
                    
        analyzed_all = False
        for pip in pips:
            for node in pip:
                content = [x for x in self.json_config["nodes"] if x["id"] == node][0]
                if content["name"].lower() == "analyze" and not analyzed_all:
                    if "heatmap" in content["data"].keys() and content["data"]["heatmap"]:
                        f.writelines("\n# **Model's Performance Heatmap**\n")
                        f.writelines("\nmetric = analyze_settings['heatmapParams']['metric']\n")
                        f.writelines("plot_p_values = analyze_settings['heatmapParams']['pValues']\n")
                        f.writelines("p_value_test = analyze_settings['heatmapParams']['pValuesMethod']\n")

                        # Other params
                        f.writelines("\nif 'title' in analyze_settings['heatmapParams'].keys() and analyze_settings['heatmapParams']['title'] is not None:\n")
                        f.writelines("    title = analyze_settings['heatmapParams']['title']\n")
                        f.writelines("else:\n")
                        f.writelines("    title = None\n")
                        f.writelines("if 'extraMetrics' in analyze_settings['heatmapParams'].keys() and analyze_settings['heatmapParams']['extraMetrics'] is not None:\n")
                        f.writelines("    stat_extra = analyze_settings['heatmapParams']['extraMetrics'].split(',')\n")
                        f.writelines("else:\n")
                        f.writelines("    stat_extra = None\n")

                        f.writelines("result.plot_heatmap(\n")
                        f.writelines("    Path(path_study), \n")
                        f.writelines("    experiment=experiment, \n")
                        f.writelines("    levels=list(set([exp_label.split('_')[1] for exp_label in experiments_labels])),\n")
                        f.writelines("    modalities=list(set([exp_label.split('_')[-1] for exp_label in experiments_labels])),\n")
                        f.writelines("    metric=metric,\n")
                        f.writelines("    stat_extra=stat_extra,\n")
                        f.writelines("    title=title,\n")
                        f.writelines("    plot_p_values=plot_p_values,\n")
                        f.writelines("    p_value_test=p_value_test,\n")
                        f.writelines("    save=False)\n")

                    # Find optimal level
                    if "optimalLevel" in content["data"].keys() and content["data"]["optimalLevel"] is not None:
                        find_optimal_level = content["data"]["optimalLevel"]
                    else:
                        find_optimal_level = False
                    if "tree" in content["data"].keys() and content["data"]["tree"] is not None:
                        plot_tree = content["data"]["tree"]
                    else:
                        plot_tree = False
                    if find_optimal_level:
                        f.writelines("\n# **Finding Optimal Level**\n")
                        f.writelines("\noptimal_levels = result.get_optimal_level(\n")
                        f.writelines("    Path(path_study), \n")
                        f.writelines("    experiment=experiment, \n")
                        f.writelines("    levels=list(set([exp_label.split('_')[1] for exp_label in experiments_labels])),\n")
                        f.writelines("    modalities=list(set([exp_label.split('_')[-1] for exp_label in experiments_labels])),\n")
                        f.writelines("    metric=metric,\n")
                        f.writelines("    p_value_test=p_value_test,\n")
                        f.writelines("    )\n")
                        f.writelines("print(optimal_levels)\n")

                        # Extra optimal level analysis
                        if plot_tree:
                            f.writelines("\n# **Tree of Importance: Extra optimal level analysis**\n")
                            f.writelines("\nmodalities = list(set([exp_label.split('_')[-1] for exp_label in experiments_labels]))\n")
                            f.writelines("for idx_m, optimal_level in enumerate(optimal_levels):\n")
                            f.writelines("    path_tree = None\n")
                            f.writelines("    if 'Text' in optimal_level:\n")
                            f.writelines("        # Plot tree\n")
                            f.writelines("        result.plot_original_level_tree(\n")
                            f.writelines("            Path(path_study), \n")
                            f.writelines("            experiment=experiment,\n")
                            f.writelines("            level=optimal_level,\n")
                            f.writelines("            modalities=[modalities[idx_m]] if len(modalities) == 1 else modalities[idx_m],\n")
                            f.writelines("            figsize=(25, 10),\n")
                            f.writelines("        )\n")
                            f.writelines("        # Get image path\n")
                            f.writelines("        path_tree = Path(path_study) / f'Original_level_{experiment}_{optimal_level}_{modalities[idx_m]}_explanation.png'\n")
                            f.writelines("\n")        
                            f.writelines("    elif 'LF' in optimal_level:\n")
                            f.writelines("        result.plot_lf_level_tree(\n")
                            f.writelines("            Path(path_study), \n")
                            f.writelines("            experiment=experiment,\n")
                            f.writelines("            level=optimal_level,\n")
                            f.writelines("            modalities=[modalities[idx_m]] if len(modalities) == 1 else modalities[idx_m],\n")
                            f.writelines("            figsize=(25, 10),\n")
                            f.writelines("        )\n")
                                
                            f.writelines("    elif 'TF' in optimal_level:\n")
                            f.writelines("        result.plot_tf_level_tree(\n")
                            f.writelines("            Path(path_study), \n")
                            f.writelines("            experiment=experiment,\n")
                            f.writelines("            level=optimal_level,\n")
                            f.writelines("            modalities=[modalities[idx_m]] if len(modalities) == 1 else modalities[idx_m],\n")
                            f.writelines("            figsize=(25, 10),\n")
                            f.writelines("        )\n")
                            f.writelines("    else:\n")
                            f.writelines("        print('The optimal level does not qualify for a Tree Analysis, Must be Texture, or Filter-Based level')\n")

                    analyzed_all = True
                    
                    # Break the loop
                    break
        
        f.close()

        f = jupytext.read(path_save_experiments / f'temp_notebook_code.py')
        jupytext.write(f, path_save_experiments / f'{"-AND-".join(piplines_all)}.ipynb', fmt='.ipynb')

        # Run the notebook
        path_notebook = path_save_experiments / f'{"-AND-".join(piplines_all)}.ipynb'

        return {"path_notebook": str(path_notebook)}

    def get_progress(self) -> dict:
        """
        Returns the progress of the pipeline execution.\n
        self._progress is a dict containing the current node in execution and the current progress of all processed nodes.\n
        this function is called by the frontend to update the progress bar continuously when the pipeline is running.

        Returns:
            dict: The progress of all pipelines execution.
        """
        return self._progress

    def set_progress(self, now: int = -1, label: str = "same") -> None:
        """
        Sets the progress of the pipeline execution.

        Args:
            now (int, optional): The current progress. Defaults to 0.
            label (str, optional): The current node in execution. Defaults to "".
        """
        if now == -1:
            now = self._progress['now']
        if label == "same":
            label = self._progress['currentLabel']
        self._progress = {'currentLabel': label, 'now': now}
import copy
import json
import os
import pickle
import pprint
import shutil
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

pp = pprint.PrettyPrinter(indent=2, compact=True, width=40, sort_dicts=False)  # allow pretty print of datatypes in console

import MEDimage
import ray

from .utils import *
from .pipeline import Pipeline
from .node import Node

# Global variables
JSON_SETTINGS_PATH = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)))) / 'settings/settings_frame.json'
UPLOAD_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))  / 'tmp'

class ExtractionWorkflow:
    def __init__(self, json_config: dict) -> None:
        self.pipelines = self.get_pipelines(json_config)

    # Temps debug function to fix pipelines
    def print_pipelines(self):
        for pipeline in self.pipelines:
            print("Pipeline:")
            for node in pipeline.nodes:
                print(node.id)
            print("\n")    
    
    def generate_pipelines(self, node_id, drawflow_scene, pipelines, nodes_list):
        # Get the home module from the drawflow scene
        home_module = drawflow_scene['Home']['data']

        # Add the node associated with node_id to the nodes_list
        if home_module[node_id]['name'] == 'extraction':
            # It the node is an extraction node, the node data is in a separate module
            node_data = drawflow_scene['extraction-' + str(node_id)]
            node_data['name'] = 'extraction'
            node_data['id'] = node_id
        else:
            node_data = home_module[node_id]
        
        nodes_list.append(Node.create_node(node_data))
        
        # If the node has output nodes, generate the pipelines starting from the output nodes
        output_nodes = home_module[node_id]['outputs']
        if output_nodes:
            for output_node_id in output_nodes["output_1"]["connections"]:
                self.generate_pipelines(output_node_id['node'], drawflow_scene, pipelines, nodes_list[:])
        else:
            # If there are no outputs it is a end node, so we create a pipeline from the nodes_list
            new_pipeline_id = len(pipelines) + 1
            
            # Create pipeline name from the node names according to old naming convention
            new_pipeline_name = "pip"
            for node in nodes_list:
                new_pipeline_name += "/" + node.id
                
            pipelines.append(Pipeline(nodes_list, new_pipeline_id, new_pipeline_name))
      
    def get_pipelines(self, json_config):
        # In the json config, get the drawflow scene
        drawflow_scene = json_config['drawflow']
        
        # In the drawflow scene, there is one Home module and zero or more extraction modules
        home_module = drawflow_scene['Home']['data']
        
        # Pass over all nodes in the home module. If the node doesnt have any inputs, it is the start of a pipeline
        pipelines = []
        for node_id in home_module:
            if not home_module[node_id]['inputs'] and home_module[node_id]['name'] == 'input':
                self.generate_pipelines(node_id, drawflow_scene, pipelines, []) # Generate the pipelines starting from an input node
        
        # Return the generated pipelines
        return pipelines
    
    def run_pipelines(self, set_progress, node_id="all"):
        results = {}
        
        # Go over each pipeline
        for pipeline in self.pipelines:
            # Run the pipeline
            res = pipeline.run(set_progress, node_id)
            
            # Get the filepath associated with the pipeline
            filepath = res["settings"]["segmentation"]["filepath"]
            
            if filepath and filepath != "":
                if filepath not in results:
                    results[filepath] = {}
                    
                # Store the pipeline results in the results dictionary under the right filename and pipeline name    
                results[filepath][pipeline.pipeline_name] = res
            
        return results
    
    def get_node_output(self, node_id):
        for pipeline in self.pipelines:
            for node in pipeline.nodes:
                if node.id == node_id:
                    return node, pipeline
        return None, None


class MEDimageExtraction:
    def __init__(self, json_config: dict) -> None:
        self.json_config = json_config # JSON config sent from the front end in the form of a dictionary
        
        self.medscan_obj = {} # Dictionary to store the MEDscan objects in the form {"filename": "MEDscan object"}
        self._progress = {'currentLabel': '', 'now': 0.0}
        self.nb_runs = 0
        self.runs = {}
    
    def __format_features(self, features_dict: dict):
        for key, value in features_dict.items():
            if (type(value) is list):
                features_dict[key] = value
            else:
                features_dict[key] = np.float64(value)
        return features_dict
    
    def __min_node_required(self, pip, node_list):
        found = False
        for node in pip:
            if pip[node]["type"] in node_list:
                found = True

        return found
    
    def __get_features_list(self, content: dict) -> list:
        if (content["name"] == "extraction"):
            features_list = []
            key = "extraction-" + str(content["id"])

            # Safety check
            if key not in self.json_config['drawflow']:
                return []

            for node_id in self.json_config['drawflow'][key]["data"]:  # We scan all node of each modulef in scene
                features_list.append(node_id)

            return features_list
        else:
            print("Node different to extraction not allowed")
            return []
    
    def __sort_features_categories(self, features_ids: list) -> list:
        """
        Sorts the features by categories

        Args:
            features_ids (list): List of features

        Returns:
            list: Features sorted by categories
        """
        features_order = ["morph", "local_intensity", "stats", "intensity_histogram", "int_vol_hist", "glcm", "glrlm", "glszm", "gldzm", "ngtdm", "ngldm"]

        # Create a dictionary of feature IDs sorted by their category name
        features_ids_dict = {feature_content["name"]: id for id in features_ids if (feature_content := get_node_content(id, self.json_config))["name"] in features_order}

        # Generate the sorted list based on the order in features_order
        return [features_ids_dict[name] for name in features_order if name in features_ids_dict]

    def get_3d_view(self):
        """
        Plots the 3D view of the volume and the ROI.
        """
        try:
            # Verify if the extraction workflow object exists and load it
            if "extractionWorkflow.pkl" in os.listdir(UPLOAD_FOLDER):
                with open(os.path.join(UPLOAD_FOLDER, "extractionWorkflow.pkl"), 'rb') as f:
                    extraction_workflow = pickle.load(f)
            else:
                return {"error": "No extraction workflow found. Please run the extraction workflow before trying to visualize it."}
            
            # Get the output of the node where the 3D view button was clicked
            node, pipeline = extraction_workflow.get_node_output(self.json_config["id"])
            
            # If the node is an input node, and is not yet in the extraction workflow, use the file name to load the MEDimage object directly
            if node is None and self.json_config["name"] == "input" and "file_loaded" in self.json_config and self.json_config["file_loaded"] != "":
                # Load the MEDimg object from the input file
                with open(UPLOAD_FOLDER / self.json_config["file_loaded"], 'rb') as f:
                    MEDimg = pickle.load(f)
                MEDimg = MEDimage.MEDscan(MEDimg)
                
                # Remove dicom header from MEDimg object as it causes errors in get_3d_view()
                # TODO: check if dicom header is needed in the future
                MEDimg.dicomH = None
                
                # View 3D image
                image_viewer(MEDimg.data.volume.array, "Input image : " + self.json_config["file_loaded"])
            else:
                node_output = node.output

                # Figure name for the 3D view
                fig_name = "Pipeline name: " + pipeline.pipeline_name + "<br>" + \
                        "Node id: " + node.id + "<br>" + \
                        "Node type: " + node.name + "\n" 
                
                # View 3D image
                image_viewer(node_output["vol"], fig_name, node_output["roi"])

            # Return success message
            return {"success": "3D view successfully plotted."}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_upload(self):
        try:
            # Check if the post request has the necessary informations
            if 'file' not in self.json_config and self.json_config['file'] != "":
                return {"error": "No file found in the configuration dict."}
            elif 'type' not in self.json_config and self.json_config['type'] != "":
                return {"error": "No type found in the configuration dict."}
            
            # Initialize the dictionary to store the file informations
            up_file_infos = {}
            
            # Check if the UPLOAD_FOLDER exists, if not create it
            if not os.path.isdir(UPLOAD_FOLDER): 
                os.makedirs(UPLOAD_FOLDER) 

            file = self.json_config["file"] # Path of the file
            file_type = self.json_config["type"] # Type of file (folder or file)

            # If the file is a folder, process the DICOM scan
            if file_type == "folder":
                # Initialize the DataManager class
                dm = MEDimage.wrangling.DataManager(path_to_dicoms=file, path_save=UPLOAD_FOLDER, save=True)

                # Process the DICOM scan
                dm.process_all_dicoms()

                # Ray shutdown for safety
                ray.shutdown()

                # Get the path to the file created by MEDimage
                file = dm.path_to_objects[0]

            # Check if the file is a valid pickle object
            if file and allowed_pickle_object(file):
                filename = os.path.basename(file)
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                # If the file is a .npy object and therefore has been processed by MEDimage, copy it to the UPLOAD_FOLDER
                if file_type == "file":
                    shutil.copy2(file, file_path)

                # Load the MEDimage pickle object to get the list of ROIs associated
                with open(file_path, 'rb') as f:
                    medscan = pickle.load(f)
                medscan = MEDimage.MEDscan(medscan)
                rois_list = medscan.data.ROI.roi_names
                
                # Return informations of instance loaded
                up_file_infos["name"] = filename
                up_file_infos["rois_list"] = rois_list
                return up_file_infos
            else:
                return {"error": "The file you tried to upload doesn't have the right format."}
        except Exception as e:
            return {"error": str(e)}
    
    def run(self) -> dict:
        try:
            # TODO : Import extraction workflow if it exists
            # Compare the current json config with the extraction workflow object
            # If the json config is different from the extraction workflow object, update the extraction workflow object
            # If the json config is the same as the extraction workflow object, use the extraction workflow object
            
            node_id = self.json_config["id"] # id of the node where the run button was clicked
            extraction_workflow = ExtractionWorkflow(self.json_config["json_scene"])
            results = extraction_workflow.run_pipelines(self.set_progress, node_id)
            
            # Pickle extraction_workflow objet and put it in the UPLOAD_FOLDER
            with open(os.path.join(UPLOAD_FOLDER, "extractionWorkflow.pkl"), 'wb') as f:
                pickle.dump(extraction_workflow, f)
                       
            return convert_np_to_py(results)

        except Exception as e:
            return {"error": str(e)}
    
    def run_all(self) -> dict:
        try:
            # TODO : Import extraction workflow if it exists
            extraction_workflow = ExtractionWorkflow(self.json_config)
            results = extraction_workflow.run_pipelines(self.set_progress)
            
            # Pickle extraction_workflow objet and put it in the UPLOAD_FOLDER
            with open(os.path.join(UPLOAD_FOLDER, "extractionWorkflow.pkl"), 'wb') as f:
                pickle.dump(extraction_workflow, f)
            
            return convert_np_to_py(results)
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_dm(self) -> dict:
        """
        Runs the DataManager instance to process all DICOM or NIFTI files in the given path.

        Returns:
            dict: The summary of the DataManager instance execution.
        """

        # Retrieve data from json request
        if "pathDicoms" in self.json_config.keys() and self.json_config["pathDicoms"] != "":
            path_to_dicoms = Path(self.json_config["pathDicoms"])
        else:
            path_to_dicoms = None
        if "pathNiftis" in self.json_config.keys() and self.json_config["pathNiftis"] != "":
            path_to_niftis = Path(self.json_config["pathNiftis"])
        else:
            path_to_niftis = None
        if "pathSave" in self.json_config.keys() and self.json_config["pathSave"] != "":
            path_save = Path(self.json_config["pathSave"])
        if "pathCSV" in self.json_config.keys() and self.json_config["pathCSV"] != "":
            path_csv = Path(self.json_config["pathCSV"])
        else:
            path_csv = None
        if "save" in self.json_config.keys():
            save = self.json_config["save"]
        if "nBatch" in self.json_config.keys():
            n_batch = self.json_config["nBatch"]

        # Check if at least one path to data is given
        if not ("pathDicoms" in self.json_config.keys() and self.json_config["pathDicoms"] != "") and not (
                "pathNiftis" in self.json_config.keys() and self.json_config["pathNiftis"] != ""):
            return {"error": "No path to data given! At least DICOM or NIFTI path must be given."}
        
        # Init DataManager instance
        try:
            dm = MEDimage.wrangling.DataManager(
            path_to_dicoms=path_to_dicoms,
            path_to_niftis=path_to_niftis,
            path_save=path_save,
            path_csv=path_csv,
            save=save, 
            n_batch=n_batch)

            # Run the DataManager
            if path_to_dicoms is not None and path_to_niftis is None:
                dm.process_all_dicoms()
            elif path_to_dicoms is None and path_to_niftis is not None:
                dm.process_all_niftis()
            else:
                dm.process_all()
            
            # Return success message
            summary = dm.summarize(return_summary=True).to_dict()
            
            # Get the number of rows
            num_rows = len(summary["count"])

            # Create a list of objects in the desired format
            result = []
            for i in range(num_rows):
                obj = {
                    "count": summary["count"][i],
                    "institution": summary["institution"][i],
                    "roi_type": summary["roi_type"][i],
                    "scan_type": summary["scan_type"][i],
                    "study": summary["study"][i]
                }
                result.append(obj)
            
        except Exception as e:
            return {"error": str(e)}

        return result

    def run_pre_checks(self) -> dict:
        """
        Runs the DataManager instance to perform pre-radiomics checks on the given DICOM or NIFTI files.

        Returns:
            dict: The summary of the DataManager instance execution.
        """

        # Data from json request
        data = self.json_config

        # Retrieve data from json request
        if "pathDicoms" in data.keys() and data["pathDicoms"] != "":
            path_to_dicoms = Path(data["pathDicoms"])
        else:
            path_to_dicoms = None
        if "pathNiftis" in data.keys() and data["pathNiftis"] != "":
            path_to_niftis = Path(data["pathNiftis"])
        else:
            path_to_niftis = None
        if "pathNpy" in data.keys() and data["pathNpy"] != "":
            path_npy = Path(data["pathNpy"])
        if "pathSave" in data.keys() and data["pathSave"] != "":
            path_save = Path(data["pathSave"])
        if "pathCSV" in data.keys() and data["pathCSV"] != "":
            path_csv = Path(data["pathCSV"])
        else:
            path_csv = None
        if "save" in data.keys():
            save = data["save"]
        if "nBatch" in data.keys():
            n_batch = data["nBatch"]
        if "wildcards_dimensions" in data.keys():
            wildcards_dimensions = data["wildcards_dimensions"]
        else:
            wildcards_dimensions = None
        if "wildcards_window" in data.keys():
            wildcards_window = data["wildcards_window"]
        else:
            wildcards_window = None
        
        # Check if wildcards are given
        if not wildcards_dimensions and not wildcards_window:
            return {"error": "No wildcards given! both wildcard for dimensions and for window must be given."}
        
        try:
            # path save (TODO: find another work-around)
            path_save_checks = Path.cwd().parent / "renderer/public/images"
            
            # Init DataManager instance
            dm = MEDimage.wrangling.DataManager(
                path_to_dicoms=path_to_dicoms,
                path_to_niftis=path_to_niftis,
                path_save=path_save,
                path_csv=path_csv,
                path_save_checks=path_save_checks,
                save=save, 
                n_batch=n_batch)

            # Run the DataManager
            dm.pre_radiomics_checks(
                path_data=path_npy,
                wildcards_dimensions=wildcards_dimensions, 
                wildcards_window=wildcards_window, 
                path_csv=path_csv,
                save=True)

            # Get pre-checks images
            # Find all png files in path
            list_png = list((path_save_checks / 'checks').glob('*.png'))
            list_titles = [png.name for png in list_png]
            list_png = [str(png) for png in list_png]
            url_list = ['.' + png.split('public')[-1].replace('\\', '/') for png in list_png]
        
        except Exception as e:
            print("\nERROR : ", str(e))
            return {"error": str(e)}
        
        # Return success message
        return {"url_list": url_list, "list_titles": list_titles, "message": "Pre-checks done successfully."}
    
    def run_be_get_json(self) -> dict:
        """
        Load the settings file and return the settings in a json format.

        Returns:
            dict: The settings in json format.
        """
        # Path json setting
        try:
            path_settings = self.json_config['selectedSettingsFile']
            settings_dict = json.load(open(path_settings, 'r'))
        except Exception as e:
            return {"error": f"PROBLEM WITH LOADING SETTINGS {str(e)}"}

        return settings_dict

    def run_be_save_json(self) -> dict:
        """
        Save the settings in a json file.

        Returns:
            dict: The success message.
        """
        try:
            # Get path
            settings = self.json_config
            path_save = settings['pathSettings']
            settings = settings['settings']
            json.dump(settings, open(path_save, 'w'), indent=4)
        except Exception as e:
            return {"error": f"PROBLEM WITH SAVING SETTINGS {str(e)}"}

        return {"success": "Settings saved successfully."}

    def run_be_count(self) -> dict:
        """
        Count the number of scans in the given path and return the number of scans and the path to save the features.

        Returns:
            dict: The number of scans and the path to save the features.
        """
        # Retrieve data from json request
        data = self.json_config
        if "path_read" in data.keys() and data["path_read"] != "":
            path_read = Path(data["path_read"])
        else:
            return {"error": "No path to read given!"}
        if "path_csv" in data.keys() and data["path_csv"] != "":
            path_csv = Path(data["path_csv"])
        else:
            return {"error": "No path to csv given!"}
        if "path_params" in data.keys() and data["path_params"] != "":
            path_params = Path(data["path_params"])
        else:
            return {"error": "No path to params given!"}
        if "path_save" in data.keys() and data["path_save"] != "":
            path_save = Path(data["path_save"])
        else:
            path_save = None

        try:
            # CSV file path process
            if str(path_csv).endswith('.csv'):
                path_csv = path_csv.parent
            
            # Load params
            with open(path_params, 'r') as f:
                params = json.load(f)
            
            # Load csv and count scans
            tabel_roi = pd.read_csv(path_csv / ('roiNames_' + params["roi_type_labels"][0] + '.csv'))
            tabel_roi['under'] = '_'
            tabel_roi['dot'] = '.'
            tabel_roi['npy'] = '.npy'
            name_patients = (pd.Series(
                tabel_roi[['PatientID', 'under', 'under',
                        'ImagingScanName',
                        'dot',
                        'ImagingModality',
                        'npy']].fillna('').values.tolist()).str.join('')).tolist()
            
            
            # Count scans in path read
            list_scans = [scan.name for scan in list(path_read.glob('*.npy'))]
            list_scans_unique = [name_patient for name_patient in name_patients if name_patient in list_scans]
            n_scans = len(list_scans_unique)

            if type(params["roi_types"]) is list:
                roi_label = params["roi_types"][0]
            else:
                roi_label = params["roi_types"]
            folder_save_path = path_save / f'features({roi_label})'
        
        except Exception as e:
            return {"error": f"PROBLEM WITH COUNTING SCANS {str(e)}"}
        
        return {"n_scans": n_scans, "folder_save_path": str(folder_save_path)}
    
    def run_be(self) -> dict:
        """
        Run the BatchExtractor instance to extract radiomics features from dataset in the given path.

        Returns:
            dict: The success message.
        """
        # Retrieve data from json request
        data = self.json_config
        if "path_read" in data.keys() and data["path_read"] != "":
            path_read = Path(data["path_read"])
        else:
            path_read = None
        if "path_save" in data.keys() and data["path_save"] != "":
            path_save = Path(data["path_save"])
        if "path_csv" in data.keys() and data["path_csv"] != "":
            path_csv = Path(data["path_csv"])
        else:
            path_csv = None
        if "path_params" in data.keys() and data["path_params"] != "":
            path_params = Path(data["path_params"])
        else:
            path_params = None
        if "n_batch" in data.keys():
            n_batch = data["n_batch"]

        try:
            # CSV file path process
            if 'csv' in path_csv.name:
                path_csv = path_csv.parent
            
            # Check if at least one path to data is given
            if not ("path_read" in data.keys() and data["path_read"] != "") and not (
                    "path_params" in data.keys() and data["path_params"] != "") and not (
                    "path_csv" in data.keys() and data["path_csv"] != ""):
                print("Multiple arguments missing")
                return {"error": "No path to data given! At least path to read, params and csv must be given."}
            
            # Init BatchExtractor instance
            be = MEDimage.biomarkers.BatchExtractor(
                path_read=path_read,
                path_csv=path_csv,
                path_params=path_params,
                path_save=path_save,
                n_batch=n_batch)

            # Run the BatchExtractor
            be.compute_radiomics()
        
        except Exception as e:
            return {"error": f"PROBLEM WITH BATCH EXTRACTION {str(e)}"}
        
        return {"success": "Radiomics features extracted successfully."}
        
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
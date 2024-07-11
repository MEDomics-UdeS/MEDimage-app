from copy import deepcopy
import numpy as np
from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class ExtractionNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.extracted_features = {}
    
    # Check if the node includes any texture features
    def includes_texture_features(self):
        texture_features_families = ["glcm", "gldzm", "glrlm", "glszm", "ngldm", "ngtdm"]
        for node in self.params:

            if self.params[node]["name"] in texture_features_families:
                return True

        return False
    
    
    # Morphological features extraction    
    def get_morph_features(self, features_to_extract, pipeline):
        try:
            features = {}

            last_feat_vol = pipeline.latest_node_output["vol"]
            last_feat_roi = pipeline.latest_node_output["roi"]
            roi_obj_morph = pipeline.latest_node_output["roi_obj_morph"]

            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.morph.extract_all(
                    vol=last_feat_vol.data,  # vol_obj.data
                    mask_int=last_feat_roi.data,  # roi_obj_morph.data,
                    mask_morph=roi_obj_morph.data,  # roi_obj_morph.data
                    res=pipeline.MEDimg.params.process.scale_non_text,
                    intensity_type=pipeline.MEDimg.params.process.intensity_type
                )

            else:
                # If only some features need to be extracted, use the name of the feature to build
                # extraction code (executed dynamically using exec()).
                for i in range(len(features_to_extract)):
                    # TODO : Would a for loop be more efficient than calling exec for each feature?
                    function_name = "MEDimage.biomarkers.morph." + str(features_to_extract[i])
                    function_params = "vol=last_feat_vol.data, mask_int=last_feat_roi.data, " \
                                    "mask_morph=last_feat_roi.data, res=MEDimg.params.process.scale_non_text"
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "last_feat_vol": last_feat_vol,
                                "last_feat_roi": last_feat_roi, "MEDimg": pipeline.MEDimg}
                    exec(function_call, global_vars, local_vars)

                    feature_name_convention = "F" + "morph" + "_" + str(features_to_extract[i])
                    features[feature_name_convention] = local_vars.get("result")
                    
            return features

        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF MORPHOLOGICAL FEATURES {str(e)}"}
    
    # Local intensity features extraction    
    def get_local_intensity_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            last_feat_vol = pipeline.latest_node_output["vol"]
            last_feat_roi = pipeline.latest_node_output["roi"]
            
            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.local_intensity.extract_all(
                    img_obj=last_feat_vol.data,  # vol_obj
                    roi_obj=last_feat_roi.data,  # roi_obj_int
                    res=pipeline.MEDimg.params.process.scale_non_text,
                    intensity_type=pipeline.MEDimg.params.process.intensity_type
                    # TODO: missing parameter that is automatically set to false
                )
            else:
                # If only some features need to be extracted, use the name of the feature to build
                # extraction code (executed dynamically using exec()).
                features = {}
                for i in range(len(features_to_extract)):
                    function_name = "MEDimage.biomarkers.local_intensity." + str(features_to_extract[i])
                    function_params = "img_obj=last_feat_vol.data, roi_obj=last_feat_roi.data, " \
                                    "res=MEDimg.params.process.scale_non_text "
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "last_feat_vol": last_feat_vol,
                                "last_feat_roi": last_feat_roi, "MEDimg": pipeline.MEDimg}
                    exec(function_call, global_vars, local_vars)

                    feature_name_convention = "Floc_" + str(features_to_extract[i])
                    features[feature_name_convention] = local_vars.get("result")
            
            return features
            
        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF LOCAL INTENSITY FEATURES {str(e)}"}
    
    # Statistical features extraction    
    def get_stats_features(self, features_to_extract, pipeline):
        try:
            last_feat_vol = pipeline.latest_node_output["vol"]
            
            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.stats.extract_all(
                    vol=last_feat_vol.data,  # vol_int_re
                    intensity_type=pipeline.MEDimg.params.process.intensity_type
                )
            else:
                # If only some features need to be extracted, use the name of the feature to build
                # extraction code (executed dynamically using exec()).
                features = {}
                for i in range(len(features_to_extract)):
                    function_name = "MEDimage.biomarkers.stats." + str(features_to_extract[i])
                    function_params = "vol=last_feat_vol"
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "last_feat_vol": last_feat_vol, "MEDimg": pipeline.MEDimg}
                    exec(function_call, global_vars, local_vars)

                    feature_name_convention = "Fstat_" + str(features_to_extract[i])
                    features[feature_name_convention] = local_vars.get("result")

            return features
            
        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF STATISTICAL FEATURES {str(e)}"}

    # Intensity histogram features extraction    
    def get_intensity_histogram_features(self, features_to_extract, pipeline):
        try:
            features = {}
            vol_quant_re = pipeline.latest_node_output["vol_quant_re_ivh"]
            
            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.intensity_histogram.extract_all(vol=vol_quant_re)
            else:
                # If only some features need to be extracted, use the name of the feature to build
                # extraction code (executed dynamically using exec()).
                for i in range(len(features_to_extract)):
                    function_name = "MEDimage.biomarkers.intensity_histogram." + str(
                        features_to_extract[i])
                    function_params = "vol=last_feat_vol"
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "last_feat_vol": vol_quant_re}
                    exec(function_call, global_vars, local_vars)

                    feature_name_convention = "Fih_" + str(features_to_extract[i])
                    features[feature_name_convention] = local_vars.get("result")

            return features

        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF INTENSITY HISTOGRAM FEATURES {str(e)}"}

    # Intensity volume histogram features extraction
    def get_int_vol_hist_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            wd = pipeline.latest_node_output["wd"]
            last_feat_vol = pipeline.latest_node_output["vol_quant_re_ivh"]
            vol_int_re = pipeline.latest_node_output["vol_int_re"]
            
            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.int_vol_hist.extract_all(
                    medscan=pipeline.MEDimg,
                    vol=last_feat_vol,  # vol_quant_re
                    vol_int_re=vol_int_re,
                    wd=wd  # TODO: Missing user_set_range argument?
                )
            else:
                # If only some features need to be extracted, use the name of the feature to build
                # extraction code (executed dynamically using exec()).
                for i in range(len(features_to_extract)):
                    function_name = "MEDimage.biomarkers.int_vol_hist." + str(features_to_extract[i])
                    function_params = "medscan=MEDimg, vol=last_feat_vol, vol_int_re=vol_int_re, wd=wd"
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "last_feat_vol": last_feat_vol,
                                "vol_int_re": vol_int_re, "MEDimg": pipeline.MEDimg, "wd": wd}
                    exec(function_call, global_vars, local_vars)

                    feature_name_convention = "Fint_vol_hist_" + str(features_to_extract[i])
                    features[feature_name_convention] = local_vars.get("result")

            return features
        
        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF INTENSITY VOLUME HISTOGRAM FEATURES {str(e)}"}


    # TODO : refactor : for node in extraction node, run node. 
    def run(self, pipeline: Pipeline):
        last_vol_compute = pipeline.latest_node_output["vol"]        
        
        # Initialize the non-texture features calculation
        pipeline.MEDimg.init_ntf_calculation(last_vol_compute)  # vol_obj
        
        for node in self.params:
            
            feature_family = self.params[node]["name"]
            features_to_extract = self.params[node]["data"]["features"]
            if feature_family == "morph":
                print("FOUND MORPH******************************************************************")
                self.extracted_features[feature_family] = self.get_morph_features(features_to_extract, pipeline)
                print(self.extracted_features)
                
            elif feature_family == "local_intensity":
                print("FOUND LOCAL INTENSITY******************************************************************")
                self.extracted_features[feature_family] = self.get_local_intensity_features(features_to_extract, pipeline)
                print(self.extracted_features)
            
            elif feature_family == "stats":
                print("FOUND STATS******************************************************************")
                self.extracted_features[feature_family] = self.get_stats_features(features_to_extract, pipeline)
                print(self.extracted_features)
            
            elif feature_family == "intensity_histogram":
                print("FOUND INTENSITY HISTOGRAM******************************************************************")
                self.extracted_features[feature_family] = self.get_intensity_histogram_features(features_to_extract, pipeline)
                print(self.extracted_features)
                
            elif feature_family == "int_vol_hist":
                print("FOUND INTENSITY VOLUME HISTOGRAM******************************************************************")
                self.extracted_features[feature_family] = self.get_int_vol_hist_features(features_to_extract, pipeline)
                print(self.extracted_features)
                
            elif feature_family == "glcm":
                print("FOUND GLCM******************************************************************")
            elif feature_family == "glrlm":
                print("FOUND GLRLM******************************************************************")
            elif feature_family == "glszm":
                print("FOUND GLSZM******************************************************************")
            elif feature_family == "gldzm":
                print("FOUND GLDZM******************************************************************")
            elif feature_family == "ngtdm":
                print("FOUND NGTDM******************************************************************")
            elif feature_family == "ngldm":
                print("FOUND NGLDM******************************************************************")
            else:
                print("Feature family : ", feature_family, "is invalid.")
            

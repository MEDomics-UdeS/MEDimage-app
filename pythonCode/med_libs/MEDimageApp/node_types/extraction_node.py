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
                    mask_int=last_feat_roi.data,  # roi_obj_int.data,
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
                    img_obj=last_feat_vol.data,  # vol_obj.data
                    roi_obj=last_feat_roi.data,  # roi_obj_int.data
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
            vol_quant_re = pipeline.latest_node_output["vol_quant_re"]
            
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


    def get_glcm_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]
            
            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.glcm.extract_all(
                    vol=vol_quant_re_texture,
                    dist_correction=pipeline.MEDimg.params.radiomics.glcm.dist_correction,
                    merge_method=pipeline.MEDimg.params.radiomics.glcm.merge_method)
            else:
                # Extracts co-occurrence matrices from the intensity roi mask prior to features
                matrices_dict = MEDimage.biomarkers.glcm.get_glcm_matrices(
                    vol_quant_re_texture,
                    merge_method=pipeline.MEDimg.params.radiomics.glcm.merge_method,
                    dist_weight_norm=pipeline.MEDimg.params.radiomics.glcm.dist_correction)

                # If not all features need to be extracted, use the name of each feature to build
                # extraction code (executed dynamically using exec()).
                for i in range(len(features_to_extract)):
                    function_name = "MEDimage.biomarkers.glcm." + str(features_to_extract[i])
                    function_params = "matrices_dict"
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "matrices_dict": matrices_dict}
                    exec(function_call, global_vars, local_vars)

                    feature_name_convention = "Fcm_" + str(features_to_extract[i])
                    features[feature_name_convention] = local_vars.get("result")
            
            return features

        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF GLCM FEATURES {str(e)}"}

    
    def get_glrlm_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]

            # TODO : temporary code used to replace single feature extraction for user
            all_features = MEDimage.biomarkers.glrlm.extract_all(
                vol=vol_quant_re_texture,
                dist_correction=pipeline.MEDimg.params.radiomics.glrlm.dist_correction,
                merge_method=pipeline.MEDimg.params.radiomics.glrlm.merge_method)

            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = all_features
            else:
                for i in range(len(features_to_extract)):
                    feature_name_convention = "Frlm_" + str(features_to_extract[i])
                    features[feature_name_convention] = all_features[feature_name_convention]

            return features
        
        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF GLRLM FEATURES {str(e)}"}
    

    def get_glszm_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]

            # TODO : temporary code used to replace single feature extraction for user
            all_features = MEDimage.biomarkers.glszm.extract_all(vol=vol_quant_re_texture)

            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = all_features
            else:
                for i in range(len(features_to_extract)):
                    feature_name_convention = "Fszm_" + str(features_to_extract[i])
                    features[feature_name_convention] = all_features[feature_name_convention]
            
            return features

        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF GLSZM FEATURES {str(e)}"}
    

    def get_gldzm_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]
            roi_obj_morph_texture = pipeline.latest_node_output_texture["roi_obj_morph"]

            # TODO : temporary code used to replace single feature extraction for user
            all_features = MEDimage.biomarkers.gldzm.extract_all(
                    vol_int=vol_quant_re_texture,
                    mask_morph=roi_obj_morph_texture.data)

            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = all_features
            else:
                for i in range(len(features_to_extract)):
                    feature_name_convention = "Fdzm_" + str(features_to_extract[i])
                    features[feature_name_convention] = all_features[feature_name_convention]

            return features
        
        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF GLDZM FEATURES {str(e)}"}
    

    def get_ngtdm_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]

            # TODO : temporary code used to replace single feature extraction for user
            all_features = MEDimage.biomarkers.ngtdm.extract_all(
                    vol=vol_quant_re_texture,
                    dist_correction=pipeline.MEDimg.params.radiomics.ngtdm.dist_correction)

            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = all_features
            else:
                for i in range(len(features_to_extract)):
                    feature_name_convention = "Fngt_" + str(features_to_extract[i])
                    features[feature_name_convention] = all_features[feature_name_convention]

            return features

        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF NGTDM FEATURES {str(e)}"}
    

    def get_ngldm_features(self, features_to_extract, pipeline):
        try:
            features = {}
            
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]
            
            # TODO : temporary code used to replace single feature extraction for user
            all_features = MEDimage.biomarkers.ngldm.extract_all(vol=vol_quant_re_texture)

            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = all_features
            else:
                features = {}
                for i in range(len(features_to_extract)):
                    feature_name_convention = "Fngl_" + str(features_to_extract[i])
                    features[feature_name_convention] = all_features[feature_name_convention]

                """ NOTE : Code to use in prevision of future MEDimage update allowing extraction of single features
                matrices_dict = MEDimage.biomarkers.ngldm.get_ngldm_matrices(
                    vol=vol_quant_re_texture)
                
                # If only some features need to be extracted, use the name of the feature to build
                # extraction code (executed dynamically using exec()).
                features = {}
                for i in range(len(features_to_extract)):
                    function_name = "MEDimage.biomarkers.ngldm." + str(features_to_extract[i])
                    function_params = "matrices_dict"
                    function_call = "result = " + function_name + "(" + function_params + ")"
                    local_vars = {}
                    global_vars = {"MEDimage": MEDimage, "matrices_dict": matrices_dict}
                    exec(function_call, global_vars, local_vars)
                    features[str(features_to_extract[i])] = local_vars.get("result")
                """

            return features

        except Exception as e:
            return {"error": f"PROBLEM WITH COMPUTATION OF NGLDM FEATURES {str(e)}"}
    

    # TODO : refactor : for node in extraction node, run node. 
    def run(self, pipeline: Pipeline):
        print("************************ RUNNING EXTRACTION ***************************")
        last_vol_compute = pipeline.latest_node_output["vol"]        
        
        # Initialize the non-texture features calculation
        pipeline.MEDimg.init_ntf_calculation(last_vol_compute)  # vol_obj
        
        # Initialize the texture features calculation
        a = 0
        n = 0
        s = 0

        pipeline.MEDimg.init_tf_calculation(
            algo=a,
            gl=n,
            scale=s)
        
        # TODO : Features wont always be in the same order
        for node in self.params:
            
            feature_family = self.params[node]["name"]
            features_to_extract = self.params[node]["data"]["features"]
            if feature_family == "morph":
                self.extracted_features[feature_family] = self.get_morph_features(features_to_extract, pipeline)
                
            elif feature_family == "local_intensity":
                self.extracted_features[feature_family] = self.get_local_intensity_features(features_to_extract, pipeline)
            
            elif feature_family == "stats":
                self.extracted_features[feature_family] = self.get_stats_features(features_to_extract, pipeline)
            
            elif feature_family == "intensity_histogram":
                 self.extracted_features[feature_family] = self.get_intensity_histogram_features(features_to_extract, pipeline)
                 
            elif feature_family == "int_vol_hist":
                 self.extracted_features[feature_family] = self.get_int_vol_hist_features(features_to_extract, pipeline)
                 
            elif feature_family == "glcm":
                self.extracted_features[feature_family] = self.get_glcm_features(features_to_extract, pipeline)

            elif feature_family == "glrlm":
                self.extracted_features[feature_family] = self.get_glrlm_features(features_to_extract, pipeline)
            
            elif feature_family == "glszm":
                self.extracted_features[feature_family] = self.get_glszm_features(features_to_extract, pipeline)
            
            elif feature_family == "gldzm":
                self.extracted_features[feature_family] = self.get_gldzm_features(features_to_extract, pipeline)
                
            elif feature_family == "ngtdm":
                self.extracted_features[feature_family] = self.get_ngtdm_features(features_to_extract, pipeline)
                
            elif feature_family == "ngldm":
                self.extracted_features[feature_family] = self.get_ngldm_features(features_to_extract, pipeline)
                
            else:
                print("Feature family : ", feature_family, "is invalid.")
            
            pipeline.scan_res = self.extracted_features

            

import MEDimage
from ..node import Node
from ..pipeline import Pipeline

class ExtractionNode(Node):
    """
    Subclass of Node that implements the extraction of radiomic features.
    """
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        
        self.extracted_features = {}  # Dictionary to store the extracted features

    def change_params(self, new_params: dict) -> None:
        """
        Change the parameters of the node.

        Args:
            new_params (dict): Dictionary containing the new parameters of the node.
            
        Returns:
            None.
        """
        self.params = new_params
        self.extracted_features = {}  # Reset the extracted features dictionary 

    def __manage_exception(self, e: Exception) -> dict:
        """
        Manages exceptions that occur during the extraction of features.

        Args:
            e (Exception): Exception that occurred during the extraction of features.

        Returns:
            dict: Dictionary containing the error message.
        """
        # Get the string representation of the exception
        string_exception = str(e)
        
        if "vol_quant_re" in string_exception:
            return {"Error": f"A discretization node needs to be in the pipeline to compute these features."}
        
        if "roi_obj_morph" in string_exception:
            return {"Error": f"An interpolation node needs to be in the pipeline to compute these features."}
        
        if "vol_int_re" in string_exception:
            return {"Error": f"A ROI extraction node needs to be in the pipeline to compute these features."}
        
        return {"Error": f"Problem with computation of features {string_exception}"}
    
    def __sort_features_by_categories(self) -> None:
        """
        Sorts the extracted features keys (features families) to always be in the same order.
       
        Args:
            None. 

        Returns:
            None.
        """
        
        features_order = ["morph", "local_intensity", "stats", "intensity_histogram", "int_vol_hist", "glcm", "glrlm", "glszm", "gldzm", "ngtdm", "ngldm"]
        
        self.extracted_features = {features: self.extracted_features[features] for features in features_order if features in self.extracted_features}
    
    def get_morph_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of morphological features.

        Args:
            features_to_extract (list[str]): List of the morphological features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted morphological features.
        """
        try:
            features = {}

            last_feat_vol = pipeline.latest_node_output["vol"]
            last_feat_roi = pipeline.latest_node_output["roi"]

            if "roi_obj_morph" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["roi_obj_morph"] is None:
                #raise Exception("roi_obj_morph")
                roi_obj_morph = last_feat_roi
            else:
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
            return self.__manage_exception(e)
    
    def get_local_intensity_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of local intensity features.

        Args:
            features_to_extract (list[str]): List of the local intensity features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted local intensity features.
        """
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
            return self.__manage_exception(e)
    
    def get_stats_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of statistical features.

        Args:
            features_to_extract (list[str]): List of the statistical features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted statistical features.
        """
        try:
            last_feat_vol = pipeline.latest_node_output["vol"]
            
            # If all features need to be extracted
            if features_to_extract[0] == "extract_all":
                features = MEDimage.biomarkers.stats.extract_all(
                    vol=last_feat_vol.data,  # vol_int_re
                    intensity_type=pipeline.MEDimg.params.process.intensity_type # Only definite type is accepted for calculating features
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
            return self.__manage_exception(e)

    def get_intensity_histogram_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of intensity histogram features.

        Args:
            features_to_extract (list[str]): List of the intensity histogram features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted intensity histogram features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output or pipeline.latest_node_output["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
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
            return self.__manage_exception(e)

    def get_int_vol_hist_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of intensity volume histogram features.

        Args:
            features_to_extract (list[str]): List of the intensity volume histogram features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted intensity volume histogram features.
        """
        try:
            features = {}
            
            if "vol_quant_re_ivh" not in pipeline.latest_node_output or pipeline.latest_node_output["vol_quant_re_ivh"] is None:
                raise Exception("vol_quant_re")
            last_feat_vol = pipeline.latest_node_output["vol_quant_re_ivh"]
            
            if "vol_int_re" not in pipeline.latest_node_output or pipeline.latest_node_output["vol_int_re"] is None:
                raise Exception("vol_int_re")
            vol_int_re = pipeline.latest_node_output["vol_int_re"]
            
            wd = pipeline.latest_node_output["wd"]
            
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
            return self.__manage_exception(e)

    def get_glcm_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of glcm features.

        Args:
            features_to_extract (list[str]): List of the glcm features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted glcm features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
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
            return self.__manage_exception(e)
    
    def get_glrlm_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of glrlm features.

        Args:
            features_to_extract (list[str]): List of the glrlm features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted glrlm features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
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
            return self.__manage_exception(e)
    
    def get_glszm_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of glszm features.

        Args:
            features_to_extract (list[str]): List of the glszm features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted glszm features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
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
            return self.__manage_exception(e)
    
    def get_gldzm_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of gldzm features.

        Args:
            features_to_extract (list[str]): List of the gldzm features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted gldzm features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
            vol_quant_re_texture = pipeline.latest_node_output_texture["vol_quant_re"]
            
            if "roi_obj_morph" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["roi_obj_morph"] is None:
                #raise Exception("roi_obj_morph")
                roi_obj_morph_texture = pipeline.latest_node_output["roi"]
            else:
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
            return self.__manage_exception(e)
    
    def get_ngtdm_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of ngtdm features.

        Args:
            features_to_extract (list[str]): List of the ngtdm features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted ngtdm features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
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
            return self.__manage_exception(e)
    
    def get_ngldm_features(self, features_to_extract: list[str], pipeline: Pipeline) -> dict:
        """
        Extraction of ngldm features.

        Args:
            features_to_extract (list[str]): List of the ngldm features to extract.
            pipeline (Pipeline): Pipeline object containing the node.

        Returns:
            dict: Dictionary containing the extracted ngldm features.
        """
        try:
            features = {}
            
            if "vol_quant_re" not in pipeline.latest_node_output_texture or pipeline.latest_node_output_texture["vol_quant_re"] is None:
                raise Exception("vol_quant_re")
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
            return self.__manage_exception(e)
    
    # TODO : refactor : for node in extraction node, run node. 
    def run(self, pipeline: Pipeline) -> None:
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
            
            # Sort the extracted features by categories
            self.__sort_features_by_categories()

            # Place the scan results in the pipeline
            pipeline.scan_res = self.extracted_features
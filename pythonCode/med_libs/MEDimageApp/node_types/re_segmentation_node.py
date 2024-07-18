from copy import deepcopy
import copy
import numpy as np
from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class ReSegmentationNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
    def run(self, pipeline: Pipeline):
        print("************************ RUNNING RE-SEGMENTATION ***************************")
        
        # 1- Compute re-segmentation for NON TEXTURE FEATURES
        ## 1.1- Get the latest volume output of the pipeline (should be the one from interpolation node)
        vol_obj = pipeline.latest_node_output["vol"]
        
        ## 1.2- Create deep copy of roi_obj_morph to avoid modifying the original object
        # TODO : Check if roi_obj_morph is present, otherwise missing interpolation node!
        roi_obj_int = deepcopy(pipeline.latest_node_output["roi_obj_morph"])
        
        ## 1.3- Intensity mask range re-segmentation (returns an ndarray)
        roi_obj_int.data = MEDimage.processing.range_re_seg(
            vol=vol_obj.data,
            roi=roi_obj_int.data,
            im_range=pipeline.MEDimg.params.process.im_range
        )        
        
        ## 1.4- Intensity mask outlier re-segmentation (returns an ndarray)
        roi_obj_int.data = np.logical_and(
            MEDimage.processing.outlier_re_seg(
                vol=vol_obj.data,
                roi=roi_obj_int.data,
                outliers=pipeline.MEDimg.params.process.outliers
            ),
            roi_obj_int.data
        ).astype(int)
        
        ## 1.5- Update the latest output object of the pipeline (only the roi was modified)
        pipeline.latest_node_output["roi"] = roi_obj_int
        # Keep a reference to roi_obj_int in the pipeline for future feature extraction
        pipeline.latest_node_output["roi_obj_int"] = roi_obj_int
        
        # 2- Compute re-segmentation for TEXTURE FEATURES
        ## 2.1- Get the latest texture volume output of the pipeline (should be the one from interpolation node)
        vol_obj_texture = pipeline.latest_node_output_texture["vol"]
        
        ## 2.2- Create deep copy of texture roi_obj_morph to avoid modifying the original object
        # TODO : Check if roi_obj_morph is present, otherwise missing interpolation node!
        roi_obj_int_texture = deepcopy(pipeline.latest_node_output_texture["roi_obj_morph"])
        
        ## 2.3- Intensity mask range re-segmentation (returns an ndarray)
        roi_obj_int_texture.data = MEDimage.processing.range_re_seg(
                vol=vol_obj_texture.data,
                roi=roi_obj_int_texture.data,
                im_range=pipeline.MEDimg.params.process.im_range
        )
        
        ## 2.4- Intensity mask outlier re-segmentation (returns an ndarray)
        roi_obj_int_texture.data = np.logical_and(
            MEDimage.processing.outlier_re_seg(
                vol=vol_obj_texture.data,
                roi=roi_obj_int_texture.data,
                outliers=pipeline.MEDimg.params.process.outliers
            ),
            roi_obj_int_texture.data
        ).astype(int)
        
        ## 2.5- Update the latest texture output object of the pipeline (only the roi was modified)
        pipeline.latest_node_output_texture["roi"] = roi_obj_int_texture
        # Keep a reference to roi_obj_int in the pipeline for future feature extraction
        pipeline.latest_node_output_texture["roi_obj_int"] = roi_obj_int_texture
        
        # 3- Update settings results of pipeline
        # If re-segmentation is not serialized, change inf to string
        if np.isinf(pipeline.MEDimg.params.process.im_range[1]):
            self.params['range'][1] = "inf"
        if np.isinf(pipeline.MEDimg.params.process.im_range[0]):
            self.params['range'][0] = "inf"      
        pipeline.settings_res["re_segmentation"] = self.params
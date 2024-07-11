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
        
        # Get the latest volume output of the pipeline (should be the one from interpolation node)
        vol_obj = pipeline.latest_node_output["vol"]
        
        # Create deep copy of roi_obj_morph to avoid modifying the original object
        #TODO : Verifier si roi_obj_morph est présent, sinon manque noeud interpolation!
        roi_obj_int = deepcopy(pipeline.latest_node_output["roi_obj_morph"])
        
        # Intensity mask re-segmentation (returns an ndarray)
        roi_obj_int.data = MEDimage.processing.range_re_seg(
            vol=vol_obj.data,
            roi=roi_obj_int.data,
            im_range=pipeline.MEDimg.params.process.im_range
        )        
        
        # Intensity mask outlier re-segmentation (returns an ndarray)
        roi_obj_int.data = np.logical_and(
            MEDimage.processing.outlier_re_seg(
                vol=vol_obj.data,
                roi=roi_obj_int.data,
                outliers=pipeline.MEDimg.params.process.outliers
            ),
            roi_obj_int.data
        ).astype(int)
        
        # Update the latest output object of the pipeline (only the roi was modified)
        pipeline.latest_node_output["roi"] = roi_obj_int
        # Keep a reference to roi_obj_int in the pipeline for future feature extraction
        pipeline.latest_node_output["roi_obj_int"] = roi_obj_int
        
        # Update settings results of pipeline
        # If re-segmentation is not serialized, change inf to string
        if np.isinf(pipeline.MEDimg.params.process.im_range[1]):
            self.params['range'][1] = "inf"
        if np.isinf(pipeline.MEDimg.params.process.im_range[0]):
            self.params['range'][0] = "inf"      
        pipeline.settings_res["re_segmentation"] = self.params
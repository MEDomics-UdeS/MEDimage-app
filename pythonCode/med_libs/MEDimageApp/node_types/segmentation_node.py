import copy
from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class SegmentationNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.selected_rois = self.params['rois_data'] # TODO : Check if rois_data is empty!!!
        
    def run(self, pipeline: Pipeline):
        #Extract the ROI mask (returns two image_volume_objects: vol_obj_init and roi_obj_init)
        vol_obj_init, roi_obj_init = MEDimage.processing.get_roi_from_indexes(
            pipeline.MEDimg,
            name_roi=self.selected_rois,
            box_string="full"
        )
        
        # Update the latest output object of the pipeline
        pipeline.latest_node_output["vol"] = vol_obj_init
        pipeline.latest_node_output["roi"] = roi_obj_init
        
        # ADDED CODE FRAGMENT FOR TEXTURE FEATURES
        # If there are some texture features to compute later, keep initial version of vol_obj_init
        # and roi_obj_init
        if pipeline.flag_texture:
            pipeline.obj_init_texture["vol"] = copy.deepcopy(vol_obj_init)
            pipeline.obj_init_texture["roi"] = copy.deepcopy(roi_obj_init)
        
        # Update settings results of the pipeline
        pipeline.settings_res['segmentation'] = self.params
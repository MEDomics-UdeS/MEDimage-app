from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class ROIExtractionNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
        
    def run(self, pipeline: Pipeline):
        print("************************ RUNNING ROI EXTRACTION ***************************")
        
        # Get the latest volume and roi output of the pipeline
        vol_obj = pipeline.latest_node_output["vol"] # comes from interpolation or filter node
        roi_obj_int = pipeline.latest_node_output["roi"] # comes from re_segmentation node
        
        # ROI extraction (returns ndarray)
        vol_int_re = MEDimage.processing.roi_extract(
            vol=vol_obj.data,
            roi=roi_obj_int.data
        )
        
        # Update the latest output object of the pipeline
        pipeline.latest_node_output["vol_int_re"] = vol_int_re

        # Update settings results of pipeline
        pipeline.settings_res["roi_extraction"] = vol_int_re        
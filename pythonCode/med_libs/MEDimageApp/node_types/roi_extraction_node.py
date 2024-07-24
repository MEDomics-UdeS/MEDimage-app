from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class ROIExtractionNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
        
    def run(self, pipeline: Pipeline):
        print("************************ RUNNING ROI EXTRACTION ***************************")
        # 1- Compute ROI extraction for NON TEXTURE FEATURES
        ## 1.1- Get the latest volume and roi output of the pipeline
        vol_obj = pipeline.latest_node_output["vol"] # comes from interpolation or filter node
        roi_obj_int = pipeline.latest_node_output["roi"] # comes from re_segmentation node
        
        ## 1.2- ROI extraction (returns ndarray)
        vol_int_re = MEDimage.processing.roi_extract(
            vol=vol_obj.data,
            roi=roi_obj_int.data
        )
        
        ## 1.3 Update the latest output object of the pipeline
        pipeline.latest_node_output["vol_int_re"] = vol_int_re

        # 2- Compute ROI extraction for TEXTURE FEATURES
        ## 2.1- Get the latest texture volume and roi output of the pipeline
        vol_obj_texture = pipeline.latest_node_output_texture["vol"] # comes from interpolation or filter node
        roi_obj_int_texture = pipeline.latest_node_output_texture["roi"] # comes from re_segmentation node

        ## 2.2- ROI extraction (returns ndarray)
        vol_int_re_texture = MEDimage.processing.roi_extract(
                vol=vol_obj_texture.data,
                roi=roi_obj_int_texture.data
        )
        
        ## 2.3 Update the latest output object of the pipeline
        pipeline.latest_node_output_texture["vol_int_re"] = vol_int_re_texture
        
        # Update the output of the node
        self.output = {"vol": vol_int_re,
                       "roi": roi_obj_int.data,
                       "vol_texture": vol_obj_texture,
                       "roi_texture": roi_obj_int_texture.data}
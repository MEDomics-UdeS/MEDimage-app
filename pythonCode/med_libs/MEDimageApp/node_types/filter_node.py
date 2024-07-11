from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class FilterNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
    def run(self, pipeline: Pipeline):        
        # Apply filter to the imaging volume
        pipeline.MEDimg.params.filter.filter_type = self.params["filter_type"] 
        vol_obj_filter = MEDimage.filters.apply_filter(
            pipeline.MEDimg, 
            pipeline.latest_node_output["vol"] # Comes from interpolation node
        )
                
        # Update the latest output object of the pipeline
        pipeline.latest_node_output["vol"] = vol_obj_filter
        
        # Update settings results of the pipeline
        pipeline.settings_res["filter"] = self.params
        
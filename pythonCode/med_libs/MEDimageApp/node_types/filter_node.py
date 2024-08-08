import MEDimage
from ..node import Node
from ..pipeline import Pipeline

class FilterNode(Node):
    """
    Subclass of Node that implements the filtering of a volume.
    """
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        
    def run(self, pipeline: Pipeline) -> None:
        print("************************ RUNNING FILTER ***************************")
        # 0- Set the correct filter type in the MEDimg object
        pipeline.MEDimg.params.filter.filter_type = self.params["filter_type"]
        
        # 1- Compute filter for NON TEXTURE FEATURES
        ## 1.1- Apply filter to the imaging volume 
        vol_obj_filter = MEDimage.filters.apply_filter(
            pipeline.MEDimg, 
            pipeline.latest_node_output["vol"] # Comes from interpolation node
        )
                
        ## 1.2 Update the latest output object of the pipeline
        pipeline.latest_node_output["vol"] = vol_obj_filter
        
        ## 1.3 Update the output of the node
        self.output = {"vol": vol_obj_filter.data,
                       "roi": pipeline.latest_node_output["roi"].data,
                       "vol_texture": None,
                       "roi_texture": None}
        
        # 2- Compute filter for TEXTURE FEATURES
        ## 2.0- Check if there is an output for texture features
        if "vol" in pipeline.latest_node_output_texture and pipeline.latest_node_output_texture["vol"] is not None:
            ## 2.1- Apply filter to the imaging volume 
            vol_obj_filter_texture = MEDimage.filters.apply_filter(
                pipeline.MEDimg, 
                pipeline.latest_node_output_texture["vol"] # Comes from interpolation node
            )
                
            ## 2.2 Update the latest output object of the pipeline
            pipeline.latest_node_output_texture["vol"] = vol_obj_filter_texture
        
            # 2.3- Update the output of the node
            self.output["vol_texture"] = vol_obj_filter_texture.data
            self.output["roi_texture"] = pipeline.latest_node_output_texture["roi"].data
        
        # 3- Update settings results of the pipeline
        pipeline.settings_res["filter"] = self.params
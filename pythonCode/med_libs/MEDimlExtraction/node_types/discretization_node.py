from copy import deepcopy

import MEDiml
from ..node import Node
from ..pipeline import Pipeline

class DiscretizationNode(Node):
    """
    Subclass of Node that implements the discretization of a volume.
    """
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        
    def run(self, pipeline: Pipeline) -> None:
        print("************************ RUNNING DISCRETIZATION ***************************")
        # Discretization for NON TEXTURE FEATURES
        # Only a roi_extraction_node can be before a discretization_node, so vol_int_re must be in the pipeline
        if "vol_int_re" in pipeline.latest_node_output and pipeline.latest_node_output["vol_int_re"] is not None:
            vol_int_re = pipeline.latest_node_output["vol_int_re"]    
        else:
            raise ValueError("No volume to discretize.")

        # Intensity discretization for IH computation (returns an ndarray and a float)
        try:
            vol_quant_re, _ = MEDiml.processing.discretisation.discretize(
                vol_re=vol_int_re,  # vol_int_re
                discr_type=pipeline.MEDimg.params.process.ih["type"],
                n_q=pipeline.MEDimg.params.process.ih["val"],
                user_set_min_val=pipeline.MEDimg.params.process.user_set_min_value, # TODO : user_set_min_val necessary for ih?
                ivh=False
            )
        except Exception as e:
            raise ValueError("Exception e", e)
        
        # Update the latest output object of the pipeline
        pipeline.latest_node_output["vol_quant_re"] = vol_quant_re 
        
        # Update the output of the node
        self.output["vol"] = deepcopy(vol_quant_re)
        self.output["roi"] = deepcopy(pipeline.latest_node_output["roi"].data)

        # Access the object once to make the code readable and faster
        ivh_params = pipeline.MEDimg.params.process.ivh
        process_params = pipeline.MEDimg.params.process

        # Check for existence and validity in a single clean step
        # Intensity discretization for IVH computation
        if ivh_params and ivh_params.get('type') and ivh_params.get('val'):
            vol_quand_re_ivh, wd = MEDiml.processing.discretisation.discretize(
                vol_re=vol_int_re,
                discr_type=ivh_params["type"],
                n_q=ivh_params["val"],
                user_set_min_val=process_params.user_set_min_value,
                ivh=True
            )
        else:
            # Handle fallback in a single place (Don't Repeat Yourself)
            vol_quand_re_ivh = deepcopy(vol_int_re)
            wd = 1

        # Update the latest output object of the pipeline
        pipeline.latest_node_output["vol_quant_re_ivh"] = vol_quand_re_ivh
        pipeline.latest_node_output["wd"] = wd
        
        # Update the output of the node
        self.output["vol_ivh"] = deepcopy(vol_quand_re_ivh)
        self.output["roi_ivh"] = deepcopy(pipeline.latest_node_output["roi"].data)
        
        # Discretization for TEXTURE FEATURES
        if "vol_int_re" in pipeline.latest_node_output_texture and pipeline.latest_node_output_texture["vol_int_re"] is not None:
            vol_int_re_texture = pipeline.latest_node_output_texture["vol_int_re"]
        else:
            vol_int_re_texture = deepcopy(vol_int_re)
            
        vol_quant_re_texture, _texture = MEDiml.processing.discretize(
                vol_re=vol_int_re_texture,
                discr_type=pipeline.MEDimg.params.process.algo[0],
                n_q=pipeline.MEDimg.params.process.gray_levels[0][0],
                user_set_min_val=pipeline.MEDimg.params.process.user_set_min_value
        )
       
        # Update the latest output texture object of the pipeline 
        pipeline.latest_node_output_texture["vol_quant_re"] = vol_quant_re_texture
       
        # Update the output of the node
        self.output["vol_texture"] = vol_quant_re_texture
        
        # Update settings results of the pipeline
        pipeline.settings_res['discretization'] = self.params
        
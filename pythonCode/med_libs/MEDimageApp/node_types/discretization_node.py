from ..node import Node
import MEDimage
from ..pipeline import Pipeline
from copy import deepcopy

class DiscretizationNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
    def run(self, pipeline: Pipeline):
        print("************************ RUNNING DISCRETIZATION ***************************")
        
        # Only a roi_extraction_node can be before a discretization_node, so vol_int_re must be in the pipeline
        if pipeline.latest_node_output["vol_int_re"] is not None:
            vol_int_re = pipeline.latest_node_output["vol_int_re"]    
        else:
            #vol_int_re = pipeline.latest_node_output["vol"]
            raise ValueError("A roi_extraction_node must be before a discretization_node")
        
        # Intensity discretisation for IH computation (returns an ndarray and a float)
        vol_quant_re, _ = MEDimage.processing.discretisation.discretize(
            vol_re=vol_int_re,  # vol_int_re
            discr_type=pipeline.MEDimg.params.process.ih["type"],
            n_q=pipeline.MEDimg.params.process.ih["val"],
            
        )
        pipeline.latest_node_output["vol_quant_re"] = vol_quant_re
        
        # Intensity discretisation for IVH computation
        if pipeline.MEDimg.params.process.ivh and 'type' in pipeline.MEDimg.params.process.ivh and 'val' in pipeline.MEDimg.params.process.ivh:
            if pipeline.MEDimg.params.process.ivh['type'] and pipeline.MEDimg.params.process.ivh['val']:
                vol_quand_re_ivh, wd = MEDimage.processing.discretisation.discretize(
                    vol_re=vol_int_re,  # vol_int_re
                    discr_type=pipeline.MEDimg.params.process.ivh["type"],
                    n_q=pipeline.MEDimg.params.process.ivh["val"],
                    user_set_min_val=pipeline.MEDimg.params.process.user_set_min_value,
                    ivh=True
                )
        else:
            vol_quand_re_ivh = deepcopy(vol_int_re)
            wd = 1
            
        print("***************************************** IVH VOL *******************************************")
        print(vol_quand_re_ivh)
        pipeline.latest_node_output["vol_quant_re_ivh"] = vol_quand_re_ivh
        pipeline.latest_node_output["wd"] = wd
        
        # Intensity discretisation for texture computation
from copy import deepcopy
from ..node import Node
import MEDimage
from ..pipeline import Pipeline

class InterpolationNode(Node):
    def __init__(self, params: dict):
        super().__init__(params)
        
    def run(self, pipeline: Pipeline):
        print("************************ RUNNING INTERPOLATION ***************************")
        # 0- Get the latest output of the pipeline and the MEDimg object
        MEDimg = pipeline.MEDimg
        last_vol_compute = pipeline.latest_node_output["vol"]
        last_roi_compute = pipeline.latest_node_output["roi"]
        
        # 1- Compute interpolation for NON TEXTURE FEATURES
        ## 1.1- Create deep copies of latest node output image_volume_object to avoid modifying the original object
        vol_obj = deepcopy(pipeline.latest_node_output["vol"])
        roi_obj_morph = deepcopy(pipeline.latest_node_output["roi"])
        vol_obj_texture = deepcopy(pipeline.latest_node_output["vol"])
        roi_obj_morph_texture = deepcopy(pipeline.latest_node_output["roi"])
        
        ## 1.2- Compute the intensity mask (returns an image_volume_object)
        vol_obj = MEDimage.processing.interp_volume(
            medscan=MEDimg,
            vol_obj_s=last_vol_compute,  # vol_obj_init,
            roi_obj_s=last_roi_compute,  # roi_obj_init
            vox_dim=MEDimg.params.process.scale_non_text,
            interp_met=MEDimg.params.process.vol_interp,
            round_val=MEDimg.params.process.gl_round,
            image_type='image',
            box_string="full" #TODO : prendre box_string de l'objet MEDimg?
        )
        
        ## 1.3- Compute the morphological mask (returns an image_volume_object)
        # The morphological mask is NOT re-segmented!
        roi_obj_morph = MEDimage.processing.interp_volume(
            medscan=MEDimg,
            vol_obj_s=last_roi_compute,  # roi_obj_init,
            roi_obj_s=last_roi_compute,  # roi_obj_init
            vox_dim=MEDimg.params.process.scale_non_text,
            interp_met=MEDimg.params.process.roi_interp,
            round_val=MEDimg.params.process.roi_pv,
            image_type='roi',
            box_string="full" #TODO : prendre box_string de l'objet MEDimg?
        )
        
        ## 1.4 Update the latest output object of the pipeline
        pipeline.latest_node_output["vol"] = vol_obj
        pipeline.latest_node_output["roi"] = roi_obj_morph
        # Keep a reference to roi_obj_morph in the pipeline for future feature extraction
        pipeline.latest_node_output["roi_obj_morph"] = roi_obj_morph
        
        # 2- Compute interpolation for TEXTURE FEATURES
        ## 2.1- Create deep copies of latest node output image_volume_object to avoid modifying the original object

        
        ## 2.2- Compute the intensity mask (returns an image_volume_object)
        vol_obj_texture = MEDimage.processing.interp_volume(
                vol_obj_s=vol_obj_texture,
                vox_dim=MEDimg.params.process.scale_text[0],
                interp_met=MEDimg.params.process.vol_interp,
                round_val=MEDimg.params.process.gl_round,
                image_type='image',
                roi_obj_s=roi_obj_morph_texture,
                box_string=MEDimg.params.process.box_string
            )
        
        ## 2.3- Compute the morphological mask (returns an image_volume_object)
        roi_obj_morph_texture = MEDimage.processing.interp_volume(
                vol_obj_s=roi_obj_morph_texture,
                vox_dim=MEDimg.params.process.scale_text[0],
                interp_met=MEDimg.params.process.roi_interp,
                round_val=MEDimg.params.process.roi_pv,
                image_type='roi',
                roi_obj_s=roi_obj_morph_texture,
                box_string=MEDimg.params.process.box_string
            )
        
        ## 2.4 Update the latest output object of the pipeline
        pipeline.latest_node_output_texture["vol"] = vol_obj_texture
        pipeline.latest_node_output_texture["roi"] = roi_obj_morph_texture
        # Keep a reference to roi_obj_morph_texture in the pipeline for future feature extraction
        pipeline.latest_node_output_texture["roi_obj_morph"] = roi_obj_morph_texture
        
        # 3- Update settings results of the pipeline
        pipeline.settings_res['interpolation'] = self.params
        
        # Update the output of the node
        self.output = {"vol": vol_obj.data,
                       "roi": roi_obj_morph.data}
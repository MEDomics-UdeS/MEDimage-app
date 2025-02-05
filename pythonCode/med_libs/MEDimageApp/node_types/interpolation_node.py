from copy import deepcopy

import MEDimage
from ..node import Node
from ..pipeline import Pipeline

class InterpolationNode(Node):
    """
    Subclass of Node that implements the interpolation of a volume.
    """
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        
    def run(self, pipeline: Pipeline) -> None:
        print("************************ RUNNING INTERPOLATION ***************************")
        # NOTE : The node before interpolation is always the segmentation node, therefore the same volume and roi objects 
        #        are used to compute the interpolation for non-texture features
        
        # Get the latest output of the pipeline and the MEDimg object
        MEDimg = pipeline.MEDimg
        last_vol_compute = pipeline.latest_node_output["vol"]
        last_roi_compute = pipeline.latest_node_output["roi"]

        # Create deep copies of latest node output image_volume_object to avoid modifying the original object
        vol_obj = deepcopy(pipeline.latest_node_output["vol"])
        roi_obj_morph = deepcopy(pipeline.latest_node_output["roi"])
        vol_obj_texture = deepcopy(pipeline.latest_node_output["vol"])
        roi_obj_morph_texture = deepcopy(pipeline.latest_node_output["roi"])
        
        # Compute interpolation for NON TEXTURE FEATURES
        ## Compute the intensity mask (returns an image_volume_object)
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
        
        ## Compute the morphological mask (returns an image_volume_object)
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
        
        ## Update the latest output object of the pipeline
        pipeline.latest_node_output["vol"] = vol_obj
        pipeline.latest_node_output["roi"] = roi_obj_morph
        # Keep a reference to roi_obj_morph in the pipeline for future feature extraction
        pipeline.latest_node_output["roi_obj_morph"] = roi_obj_morph
        
        # Compute interpolation for TEXTURE FEATURES
        ## Compute the intensity mask (returns an image_volume_object)
        vol_obj_texture = MEDimage.processing.interp_volume(
                vol_obj_s=vol_obj_texture,
                vox_dim=MEDimg.params.process.scale_text[0],
                interp_met=MEDimg.params.process.vol_interp,
                round_val=MEDimg.params.process.gl_round,
                image_type='image',
                roi_obj_s=roi_obj_morph_texture,
                box_string=MEDimg.params.process.box_string
            )
        
        ## Compute the morphological mask (returns an image_volume_object)
        roi_obj_morph_texture = MEDimage.processing.interp_volume(
                vol_obj_s=roi_obj_morph_texture,
                vox_dim=MEDimg.params.process.scale_text[0],
                interp_met=MEDimg.params.process.roi_interp,
                round_val=MEDimg.params.process.roi_pv,
                image_type='roi',
                roi_obj_s=roi_obj_morph_texture,
                box_string=MEDimg.params.process.box_string
            )
        
        ## Update the latest output object of the pipeline
        pipeline.latest_node_output_texture["vol"] = vol_obj_texture
        pipeline.latest_node_output_texture["roi"] = roi_obj_morph_texture
        # Keep a reference to roi_obj_morph_texture in the pipeline for future feature extraction
        pipeline.latest_node_output_texture["roi_obj_morph"] = roi_obj_morph_texture

        # Update the output of the node
        self.output = {"vol": vol_obj.data,
                       "roi": roi_obj_morph.data,
                       "vol_texture": vol_obj_texture.data,
                       "roi_texture": roi_obj_morph_texture.data}
        
        # Update settings results of the pipeline
        pipeline.settings_res['interpolation'] = self.params
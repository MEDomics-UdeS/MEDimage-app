from .node import Node
from typing import List
import os
from pathlib import Path
import MEDimage

JSON_SETTINGS_PATH = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)))) / 'settings/settings_frame.json'
class Pipeline:
    def __init__(self, nodes: List[Node], pipeline_id: int):
        self.nodes = nodes # List of nodes object in the pipeline
        self.pipeline_id = pipeline_id # ID of the pipeline
    
        self.flag_texture = False # Flag to check if the pipeline includes texture features
        if nodes[-1].name and nodes[-1].name == "extraction" and nodes[-1].includes_texture_features():
            self.flag_texture = True
            
        self.MEDimg = None # MEDimg object of the input image
        self.latest_node_output = {} # Output of the latest node in the pipeline
        self.obj_init_texture = {} # Output of segmentation node to keep initial version of vol_obj_init and roi_obj_init for texture features
        
        self.settings_res = {} # Dictionary to store the settings results of the pipeline
        self.scan_res = {} # Dictionary to store the scan results (radiomics)
    
        # Loading default settings from MEDimageApp json file as im_params
        self.im_params = MEDimage.utils.json_utils.load_json(JSON_SETTINGS_PATH)


    def get_previous_node_output(self, node: Node):
        """ Given a node, return the output of the previous node in the pipeline

        Args:
            node (Node): the node for which to get the previous output
        """
        prev = [self.nodes[i-1] for i in range(len(self.nodes)) if self.nodes[i].id == node.id]
        if prev:
            return prev[0].output
        else:
            return None
        
    
    def get_node_output_from_type(self, node_name: str):
        """ Checks if a node with the given name exists in the pipeline and returns its output

        Args:
            node_name (str): _description_

        Returns:
            _type_: _description_
        """
        for node in self.nodes:
            if node.name == node_name:
                return node.output
        return {"error": f"Node not found in pipeline."} # TODO : Bonne facon de retourner error?
    
    
    def update_im_params(self):
        """ Update the im_params dictionnary with the parameters of the nodes in the pipeline.
            im_params is a dictionnary that contains the parameters of the image processing pipeline
            in the format used by MEDimage.
        """
        scan_type = self.nodes[0].scan_type # Get the scan type from the input node
        
        for node in self.nodes:
            if (node.name == "filter"):
                self.im_params["imParamFilter"] = node.params
                
            elif (node.name == "interpolation"):
                self.im_params[scan_type]["interp"] = node.params

            elif (node.name == "re_segmentation"):
                self.im_params[scan_type]["reSeg"] = node.params

            elif (node.name == "discretization"):
                self.im_params[scan_type]["discretisation"] = node.params

    
    def run(self, node_id: str = "all"):
        for node in self.nodes:
            node.run(self)
            if node.id == node_id:
                break
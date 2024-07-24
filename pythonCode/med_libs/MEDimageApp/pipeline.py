from .node import Node
from typing import List
import os
from pathlib import Path
import MEDimage

JSON_SETTINGS_PATH = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)))) / 'settings/settings_frame.json'
class Pipeline:
    def __init__(self, nodes: List[Node], pipeline_id: int, pipeline_name: str):
        self.nodes = nodes # List of nodes object in the pipeline
        self.pipeline_id = pipeline_id # ID of the pipeline
        self.pipeline_name = pipeline_name # Name of the pipeline
            
        self.MEDimg = None # MEDimg object of the input image
        self.latest_node_output = {} # Output of the latest node in the pipeline (used for non texture features)
        self.latest_node_output_texture = {} # Output of the latest node in the pipeline (used for texture features)
        
        self.settings_res = {} # Dictionary to store the settings results of the pipeline
        self.scan_res = {} # Dictionary to store the scan results (radiomics)
    
        
        self.im_params = MEDimage.utils.json_utils.load_json(JSON_SETTINGS_PATH) # Loading default settings from MEDimageApp json file as im_params


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

    
    def run(self, set_progress, node_id: str = "all"):
        # The pipeline is starting, set the progress to 0%
        set_progress(now=0.0, label=f"Starting pipeline : " + self.pipeline_name)
        
        # Number of nodes in the pipeline
        number_nodes = len(self.nodes)
        # Number of the current node 
        node_number = 1.0 

        for node in self.nodes:
            # Run the node
            node.run(self)
            # Update the progress bar
            set_progress(now=node_number * 100 / number_nodes, label=f"Pipeline " + self.pipeline_name + " | Running node : " + node.name)
            # Increment the node number
            node_number += 1.0
            
            if node.id == node_id:
                break
        
        # Create the results dictionnary
        results = {"features": self.scan_res, 
                   "settings": self.settings_res}
        
        # Reset the latest node output
        self.latest_node_output = {}
        self.latest_node_output_texture = {}
        
        # The pipeline is done executing, set the progress to 100%
        set_progress(now=100.0, label=f"Ending pipeline : " + self.pipeline_name)
        
        return results
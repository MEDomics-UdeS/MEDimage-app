from .node import Node
from typing import List
import copy
import os
from pathlib import Path
import MEDimage
from .node_types.filter_node import FilterNode
from .node_types.interpolation_node import InterpolationNode
from .node_types.re_segmentation_node import ReSegmentationNode
from .node_types.discretization_node import DiscretizationNode 


JSON_SETTINGS_PATH = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)))) / 'settings/settings_frame.json'
class Pipeline:
    def __init__(self, nodes: List[Node], pipeline_id: int):
        self.nodes = nodes # List of nodes object in the pipeline
        self.pipeline_id = pipeline_id
        
        self.nb_runs = 0
        self.runs = {}
    
        self.flag_texture = False
        
        self.node_outputs = {} # Dictionary to store the output of each node
        self.scan_results = {} # Dictionary to store the scan results (radiomics)
    
        # Loading default settings from MEDimageApp json file as im_params
        self.im_params = MEDimage.utils.json_utils.load_json(JSON_SETTINGS_PATH)

        # If the first node is an input node update im_params to correspond with scan type
        #if self.nodes[0].__class__.__name__ == "InputNode":
            # Update image parameters of the pipeline using the data from it's nodes
        #    self.im_params = self.__update_im_params()

    def update_im_params(self):
        scan_type = self.nodes[0].scan_type # Get the scan type from the input node
        for node in self.nodes:
            # FILTERING
            if (isinstance(node, FilterNode)):
                self.im_params["imParamFilter"] = node.params
                
            # INTERPOLATION
            elif (isinstance(node, InterpolationNode)):
                self.im_params[scan_type]["interp"] = node.params

            # RE-SEGMENTATION
            elif (isinstance(node, ReSegmentationNode)):
                self.im_params[scan_type]["reSeg"] = node.params

            # DISCRETIZATION
            elif (isinstance(node, DiscretizationNode)):
                self.im_params[scan_type]["discretisation"] = node.params

    
    def run(self, node_id: str = "all"):
        for node in self.nodes:
            node.run(self)
            if node.id == node_id:
                break
    
        self.nb_runs += 1 # Incrementing the number of runs
        self.runs[self.nb_runs] = copy.deepcopy(self.scan_results) # Storing the scan results in the runs dictionary
        self.scan_results = {} # Reset scan_results for the next run
from ..node import Node
import MEDimage

class SegmentationNode(Node):
    def __init__(self, params: dict):
        self.id = params['id']
        
        self.selected_rois = params['data']['rois_data']
        
    def run(self, pipeline_params: dict):        
        pass
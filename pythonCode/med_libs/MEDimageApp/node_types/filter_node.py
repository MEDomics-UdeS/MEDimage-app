from ..node import Node
import MEDimage

class FilterNode(Node):
    def __init__(self, params: dict):
        self.id = params['id']
        
        self.params = params['data']
        
    def run(self, pipeline_params: dict):        
        pass
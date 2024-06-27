from ..node import Node
import MEDimage

class ExtractionNode(Node):
    def __init__(self, params: dict):
        self.id = params['id']
        
        #Doit gérer les features sélectionnés.
        
    def run(self, pipeline_params: dict):        
        pass
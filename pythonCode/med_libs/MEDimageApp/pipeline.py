from typing import List
from .node import Node

class Pipeline:
    def __init__(self, nodes: List[Node], pipeline_id: int):
        self.nodes = nodes
        self.pipeline_id = pipeline_id
        
        self.nb_runs = 0
        self.runs = {}
    
        self.flag_texture = False
    
    def run(self):
        for node in self.nodes:
            node.run()
    
    
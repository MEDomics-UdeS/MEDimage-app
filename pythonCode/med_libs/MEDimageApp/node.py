from abc import ABC, abstractmethod

import numpy as np

class Node(ABC):
    @abstractmethod
    def run(self):
        pass
    
    @staticmethod
    def createNode(node_data: dict):
        print("Creating node with ID: " + str(node_data["id"]))
        return {"id": node_data["id"]}
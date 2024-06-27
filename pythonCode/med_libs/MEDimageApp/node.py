from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def run(self, pipeline):
        pass
    
    # TODO : REFACTOR AVEC FACTORY METHOD
    @staticmethod
    def create_node(node_data: dict):
        print('Creating node with ID: ' + str(node_data['id']))
        node_type = node_data["name"]
        if node_type == 'input':
            from .node_types.input_node import InputNode
            return InputNode(node_data)
        elif node_type == 'segmentation':
            from .node_types.segmentation_node import SegmentationNode
            return SegmentationNode(node_data)
        elif node_type == 'interpolation':
            from .node_types.interpolation_node import InterpolationNode    
            return InterpolationNode(node_data)
        elif node_type == 'filter':
            from .node_types.filter_node import FilterNode
            return FilterNode(node_data)
        elif node_type == 're_segmentation':
            from .node_types.re_segmentation_node import ReSegmentationNode
            return ReSegmentationNode(node_data)
        elif node_type == 'roi_extraction':
            from .node_types.roi_extraction_node import ROIExtractionNode
            return ROIExtractionNode(node_data)
        elif node_type == 'discretization':
            from .node_types.discretization_node import DiscretizationNode
            return DiscretizationNode(node_data)
        elif node_type == 'extraction':
            from .node_types.extraction_node import ExtractionNode
            return ExtractionNode(node_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
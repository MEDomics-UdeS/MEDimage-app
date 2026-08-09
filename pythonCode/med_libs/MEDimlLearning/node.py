from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .context import LearningContext


class LearningNode(ABC):
    """Base class for all learning nodes."""

    node_type: str = "node"

    def __init__(self, params: dict[str, Any]) -> None:
        self.name = params["name"]
        self.id = params["id"]
        self.params = params.get("data", {})
        self.output: dict[str, Any] = {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LearningNode) and self.id == other.id

    def change_params(self, new_params: dict[str, Any]) -> None:
        self.params = new_params

    @abstractmethod
    def run(self, context: LearningContext) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_code(self, file_obj, settings: dict[str, Any]) -> None:
        raise NotImplementedError

    def _write_lines(self, file_obj, lines: list[str]) -> None:
        for line in lines:
            file_obj.write(f"{line}\n")

    @staticmethod
    def create_node(node_data: dict[str, Any]) -> "LearningNode":
        node_type = node_data["name"].lower()
        if node_type == "split":
            from .node_types.split_node import SplitNode

            return SplitNode(node_data)
        if node_type == "design":
            from .node_types.design_node import DesignNode

            return DesignNode(node_data)
        if node_type == "data":
            from .node_types.data_node import DataNode

            return DataNode(node_data)
        if node_type == "cleaning":
            from .node_types.cleaning_node import CleaningNode

            return CleaningNode(node_data)
        if node_type == "normalization":
            from .node_types.normalization_node import NormalizationNode

            return NormalizationNode(node_data)
        if node_type == "feature_reduction":
            from .node_types.feature_reduction_node import FeatureReductionNode

            return FeatureReductionNode(node_data)
        if node_type == "radiomics_learner":
            from .node_types.radiomics_learner_node import RadiomicsLearnerNode

            return RadiomicsLearnerNode(node_data)
        if node_type == "analyze":
            from .node_types.analyze_node import AnalyzeNode

            return AnalyzeNode(node_data)
        raise ValueError(f"Unknown node type: {node_data['name']}")

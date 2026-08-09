from __future__ import annotations

from pathlib import Path
from typing import Any

from ..context import LearningContext
from ..node import LearningNode


class SplitNode(LearningNode):
    node_type = "split"

    def run(self, context: LearningContext) -> None:
        context.split_settings = dict(self.params)
        context.design_settings = {"design": dict(self.params)}
        context.experiment_label = self.params["expName"]
        context.path_settings = self._resolve_settings_path()
        context.paths_splits = []
        context.split_counter = 0
        active_methods = self.params.get("active_method", [])
        active_method = active_methods[0].lower() if active_methods else ""
        if active_method == "cv":
            context.nb_split = self.params.get("cv", {}).get("nFolds", 5)
        elif active_method == "random":
            context.nb_split = self.params.get("random", {}).get("nSplits", 10)
        else:
            context.nb_split = 5
        context.designed_experiment = False
        context.splitted_data = False

    def _resolve_settings_path(self) -> Path:
        return Path.cwd() / "baseFiles" / "ml_settings.yml"

    def generate_code(self, file_obj, settings: dict[str, Any]) -> None:
        self._write_lines(
            file_obj,
            [
                "# Split",
                f"split_settings = {settings!r}",
                "design_settings = {'design': dict(split_settings)}",
                "experiment_label = split_settings['expName']",
                "path_settings = Path.cwd() / 'baseFiles' / 'ml_settings.yml'",
                "paths_splits = []",
                "split_counter = 0",
                "active_methods = split_settings.get('active_method', [])",
                "active_method = active_methods[0].lower() if active_methods else ''",
                "if active_method == 'cv':",
                "    nb_split = split_settings.get('cv', {}).get('nFolds', 5)",
                "elif active_method == 'random':",
                "    nb_split = split_settings.get('random', {}).get('nSplits', 10)",
                "else:",
                "    nb_split = 5",
                "designed_experiment = False",
                "splitted_data = False",
            ],
        )

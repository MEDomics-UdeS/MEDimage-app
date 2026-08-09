from __future__ import annotations

from pathlib import Path
from typing import Any

import MEDiml

from ..context import LearningContext
from ..node import LearningNode


class DesignNode(LearningNode):
    node_type = "design"

    def run(self, context: LearningContext) -> None:
        context.path_outcome_file = Path(self.params["path_outcome_file"])
        context.path_ws_experiments = Path(self.params["path_ws_experiments"])
        context.path_save_experiments = Path(self.params["path_save_experiments"])
        context.outcome_name = self.params["outcome_name"]
        context.method = self.params["method"]
        context.holdout_test = context.method != "all_learn"
        context.evaluate_holdout = context.holdout_test

        path_study = MEDiml.learning.ml_utils.create_holdout_set(
            path_outcome_file=context.path_outcome_file,
            path_save_experiments=context.path_save_experiments,
            outcome_name=context.outcome_name,
            method=context.method,
        )
        context.path_study = Path(path_study) if not isinstance(path_study, Path) else path_study

        experiment = MEDiml.learning.DesignExperiment(
            context.path_study,
            context.path_ws_experiments,
            context.path_settings,
            context.experiment_label,
        )

        experiment_dict = experiment.create_experiment(context.design_settings)

        context.paths_splits = [experiment_dict[run] for run in experiment_dict.keys()]
        context.split_counter = 0
        context.designed_experiment = True
        context.splitted_data = True

    def generate_code(self, file_obj, settings: dict[str, Any]) -> None:
        self._write_lines(
            file_obj,
            [
                "# Design",
                f"design_settings.update({settings!r})",
                "path_outcome_file = Path(design_settings['path_outcome_file'])",
                "path_ws_experiments = Path(design_settings['path_ws_experiments'])",
                "path_save_experiments = Path(design_settings['path_save_experiments'])",
                "outcome_name = design_settings['outcome_name']",
                "method = design_settings['method']",
                "holdout_test = method != 'all_learn'",
                "evaluate_holdout = holdout_test",
                "path_study = MEDiml.learning.ml_utils.create_holdout_set(",
                "    path_outcome_file=path_outcome_file,",
                "    path_save_experiments=path_save_experiments,",
                "    outcome_name=outcome_name,",
                "    method=method",
                ")",
                "path_study = Path(path_study) if not isinstance(path_study, Path) else path_study",
                "experiment = MEDiml.learning.DesignExperiment(path_study, path_ws_experiments, path_settings, experiment_label)",
                "experiment_dict = experiment.create_experiment(design_settings)",
                "paths_splits = [experiment_dict[run] for run in experiment_dict.keys()]",
                "split_counter = 0",
                "designed_experiment = True",
                "splitted_data = True",
            ],
        )
     
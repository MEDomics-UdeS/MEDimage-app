from __future__ import annotations

from pathlib import Path
from typing import Any

import MEDiml
import pandas as pd

from ..context import LearningContext
from ..node import LearningNode


class DataNode(LearningNode):
    node_type = "data"

    def run(self, context: LearningContext) -> None:
        context.data_settings = dict(self.params)

        if context.current_split_path is None:
            raise ValueError("Data node requires a split path. Run split/design nodes first.")

        context.ml_dict_paths = MEDiml.utils.load_json(context.current_split_path)
        context.patients_train = MEDiml.utils.load_json(context.ml_dict_paths["patientsTrain"])
        context.patients_test = MEDiml.utils.load_json(context.ml_dict_paths["patientsTest"])

        outcome_table = pd.read_csv(context.ml_dict_paths["outcomes"], index_col=0)
        context.outcome_table_binary = outcome_table.iloc[:, [0]]
        if outcome_table.shape[1] == 2:
            context.extras["outcome_table_time"] = outcome_table.iloc[:, [1]]

        context.path_results = Path(context.ml_dict_paths["results"])
        context.patient_ids = list(context.outcome_table_binary.index)
        context.outcome_table_binary_training = context.outcome_table_binary.loc[context.patients_train]

        context.patients_holdout = None
        if context.holdout_test:
            holdout_path = context.path_study / "patientsHoldOut.json" if context.path_study is not None else None
            if holdout_path and holdout_path.exists():
                context.patients_holdout = MEDiml.utils.load_json(holdout_path)
            else:
                context.evaluate_holdout = False

        context.rad_var_struct = {"path": {}}
        name_type = self.params.get("nameType", "radiomics") or "radiomics"
        if "radiomics" not in name_type.lower():
            raise TypeError("Data node: Only Radiomics variables are supported!")

        path_features = Path(self.params["path"])
        features_files = self.params["featuresFiles"]
        for file_name in features_files:
            if not file_name.endswith(".csv"):
                raise TypeError("Data node: Only csv files are supported!")

        for index, feature_file in enumerate(features_files, start=1):
            rad_tab_x = {
                "csv": path_features / feature_file,
                "txt": path_features / (feature_file.split(".")[0] + ".txt"),
                "type": feature_file.split("__")[1].split("_")[0] if "__" in feature_file else "None",
            }
            if not rad_tab_x["csv"].exists():
                raise FileNotFoundError(f"File {rad_tab_x['csv']} does not exist.")
            if not rad_tab_x["txt"].exists():
                raise FileNotFoundError(f"File {rad_tab_x['txt']} does not exist.")
            context.rad_var_struct["path"][f"radTab{index}"] = rad_tab_x

        context.loaded_data = True

    def generate_code(self, file_obj, settings: dict[str, Any]) -> None:
        self._write_lines(
            file_obj,
            [
                "# Data",
                f"data_settings = {settings!r}",
                "if path_ml is None:",
                "    raise ValueError('Data node requires a split path. Run split/design nodes first.')",
                "ml_dict_paths = MEDiml.utils.load_json(path_ml)",
                "patients_train = MEDiml.utils.load_json(ml_dict_paths['patientsTrain'])",
                "patients_test = MEDiml.utils.load_json(ml_dict_paths['patientsTest'])",
                "outcome_table = pd.read_csv(ml_dict_paths['outcomes'], index_col=0)",
                "outcome_table_binary = outcome_table.iloc[:, [0]]",
                "if outcome_table.shape[1] == 2:",
                "    outcome_table_time = outcome_table.iloc[:, [1]]",
                "path_results = ml_dict_paths['results']",
                "patient_ids = list(outcome_table_binary.index)",
                "outcome_table_binary_training = outcome_table_binary.loc[patients_train]",
                "patients_holdout = None",
                "if holdout_test:",
                "    holdout_path = path_study / 'patientsHoldOut.json' if path_study is not None else None",
                "    if holdout_path and holdout_path.exists():",
                "        patients_holdout = MEDiml.utils.load_json(holdout_path)",
                "    else:",
                "        evaluate_holdout = False",
                "rad_var_struct = {'path': {}}",
                "name_type = data_settings.get('nameType', 'radiomics') or 'radiomics'",
                "if 'radiomics' not in name_type.lower():",
                "    raise TypeError('Data node: Only Radiomics variables are supported!')",
                "path_features = Path(data_settings['path'])",
                "features_files = data_settings['featuresFiles']",
                "for file_name in features_files:",
                "    if not file_name.endswith('.csv'):",
                "        raise TypeError('Data node: Only csv files are supported!')",
                "for index, feature_file in enumerate(features_files, start=1):",
                "    rad_tab_x = {",
                "        'csv': path_features / feature_file,",
                "        'txt': path_features / (feature_file.split('.')[0] + '.txt'),",
                "        'type': feature_file.split('__')[1].split('_')[0] if '__' in feature_file else 'None',",
                "    }",
                "    if not rad_tab_x['csv'].exists():",
                "        raise FileNotFoundError(f\"File {rad_tab_x['csv']} does not exist.\")",
                "    if not rad_tab_x['txt'].exists():",
                "        raise FileNotFoundError(f\"File {rad_tab_x['txt']} does not exist.\")",
                "    rad_var_struct['path'][f'radTab{index}'] = rad_tab_x",
                "loaded_data = True",
            ],
        )

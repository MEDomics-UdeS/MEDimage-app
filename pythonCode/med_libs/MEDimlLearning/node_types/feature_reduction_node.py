from __future__ import annotations

from copy import deepcopy
from typing import Any

import MEDiml

from ..context import LearningContext
from ..node import LearningNode


class FeatureReductionNode(LearningNode):
    node_type = "feature_reduction"

    def run(self, context: LearningContext) -> None:
        context.fsr_settings = dict(self.params)
        if not context.loaded_data:
            raise ValueError("Cleaning: Data must be loaded first. Use the Data node.")

        if not context.cleaned_data and not context.normalized_features:
            context.rad_tables_learning = []
            for item in context.rad_var_struct["path"].values():
                path_radiomics_csv = item["csv"]
                path_radiomics_txt = item["txt"]
                image_type = item["type"]
                rad_table_learning = MEDiml.learning.ml_utils.get_radiomics_table(
                    path_radiomics_csv,
                    path_radiomics_txt,
                    image_type,
                    context.patient_ids,
                )
                context.rad_tables_learning.append(rad_table_learning)

        context.rad_tables_testing = deepcopy(context.rad_tables_learning)
        context.rad_tables_training = []
        for rad_tab in context.rad_tables_learning:
            patients_ids = MEDiml.learning.ml_utils.intersect(context.patients_train, list(rad_tab.index))
            context.rad_tables_training.append(deepcopy(rad_tab.loc[patients_ids]))

        # Deepcopy properties
        temp_properties = list()
        for rad_tab in context.rad_tables_testing:
            temp_properties.append(deepcopy(rad_tab.Properties))

        f_set_reduction_method = context.fsr_settings.get("method", "FDA")
        if f_set_reduction_method.lower() != "fda":
            raise ValueError("Feature Reduction: Method not implemented yet (check FSR class).")

        fsr_dict = {"fSetReduction": {"FDA": context.fsr_settings["FDA"]}}
        fsr = MEDiml.learning.FSR(f_set_reduction_method)

        context.rad_tables_training = fsr.apply_fsr(
            fsr_dict,
            context.rad_tables_training,
            context.outcome_table_binary_training,
            path_save_logging=str(context.path_results) if context.path_results is not None else None,
        )

        # Re-assign properties
        for i in range(len(context.rad_tables_testing)):
            context.rad_tables_testing[i].Properties = temp_properties[i]
        del temp_properties

        context.rad_tables_testing = MEDiml.learning.ml_utils.combine_rad_tables(context.rad_tables_testing)
        context.reduced_features = True

    def generate_code(self, file_obj, settings: dict[str, Any]) -> None:
        self._write_lines(
            file_obj,
            [
                "# Feature reduction",
                f"fsr_settings = {settings!r}",
                "if not rad_var_struct.get('path'):",
                "    raise ValueError('Cleaning: Data must be loaded first. Use the Data node.')",
                "if not cleaned_data and not normalized_features:",
                "    rad_tables_learning = []",
                "    for item in rad_var_struct['path'].values():",
                "        path_radiomics_csv = item['csv']",
                "        path_radiomics_txt = item['txt']",
                "        image_type = item['type']",
                "        rad_table_learning = MEDiml.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)",
                "        rad_tables_learning.append(rad_table_learning)",
                "rad_tables_testing = deepcopy(rad_tables_learning)",
                "rad_tables_training = []",
                "for rad_tab in rad_tables_learning:",
                "    patients_ids = MEDiml.learning.ml_utils.intersect(patients_train, list(rad_tab.index))",
                "    rad_tables_training.append(deepcopy(rad_tab.loc[patients_ids]))",
                "temp_properties = [deepcopy(rad_tab.Properties) for rad_tab in rad_tables_testing]",
                "f_set_reduction_method = fsr_settings['method']",
                "if f_set_reduction_method.lower() != 'fda':",
                "    raise ValueError('Feature Reduction: Method not implemented yet (check FSR class).')",
                "fsr_dict = {'fSetReduction': {'FDA': fsr_settings['FDA']}}",
                "fsr = MEDiml.learning.FSR(f_set_reduction_method)",
                "rad_tables_training = fsr.apply_fsr(fsr_dict, rad_tables_training, outcome_table_binary_training, path_save_logging=str(path_results) if path_results is not None else None)",
                "for i in range(len(rad_tables_testing)):",
                "    rad_tables_testing[i].Properties = temp_properties[i]",
                "rad_tables_testing = MEDiml.learning.ml_utils.combine_rad_tables(rad_tables_testing)",
                "reduced_features = True",
            ],
        )

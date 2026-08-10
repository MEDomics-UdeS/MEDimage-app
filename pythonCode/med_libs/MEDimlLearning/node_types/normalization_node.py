from __future__ import annotations

from typing import Any

from copy import deepcopy

import MEDiml

from ..context import LearningContext
from ..node import LearningNode


class NormalizationNode(LearningNode):
    node_type = "normalization"

    def run(self, context: LearningContext) -> None:
        context.normalization_settings = dict(self.params)
        if not context.loaded_data:
            raise ValueError("Cleaning: Data must be loaded first. Use the Data node.")

        normalization_method = context.normalization_settings.get("method", "")

        if not context.cleaned_data:
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

        if "combat" not in normalization_method.lower():
            raise ValueError(f"Normalization: method {normalization_method} not implemented yet!")

        for index, rad_table_learning in enumerate(context.rad_tables_learning):
            rad_table_learning.Properties.setdefault("userData", {})
            rad_table_learning.Properties["userData"]["normalization"] = {"original_data": {}}
            original_data = rad_table_learning.Properties["userData"]["normalization"]["original_data"]
            original_data["patient_ids"] = context.patient_ids
            if context.cleaned_data:
                original_data["datacleaning_method"] = next(iter(context.cleaning_settings.keys()), None)

            normalization = MEDiml.learning.Normalization.CombatNormalization()
            context.rad_tables_learning[index] = normalization.fit_transform(rad_table_learning)

        context.normalized_features = True

    def generate_code(self, file_obj, settings: dict[str, Any]) -> None:
        self._write_lines(
            file_obj,
            [
                "# Normalization",
                f"normalization_settings = {settings!r}",
                "if not rad_var_struct.get('path'):",
                "    raise ValueError('Cleaning: Data must be loaded first. Use the Data node.')",
                "normalization_method = normalization_settings['method']",
                "if not cleaned_data:",
                "    rad_tables_learning = []",
                "    for item in rad_var_struct['path'].values():",
                "        path_radiomics_csv = item['csv']",
                "        path_radiomics_txt = item['txt']",
                "        image_type = item['type']",
                "        rad_table_learning = MEDiml.learning.ml_utils.get_radiomics_table(path_radiomics_csv, path_radiomics_txt, image_type, patient_ids)",
                "        rad_tables_learning.append(rad_table_learning)",
                "if 'combat' not in normalization_method.lower():",
                "    raise ValueError(f'Normalization: method {normalization_method} not implemented yet!')",
                "for index, rad_table_learning in enumerate(rad_tables_learning):",
                "    rad_table_learning.Properties.setdefault('userData', {})",
                "    rad_table_learning.Properties['userData']['normalization'] = {'original_data': {}}",
                "    original_data = rad_table_learning.Properties['userData']['normalization']['original_data']",
                "    original_data['patient_ids'] = patient_ids",
                "    if cleaned_data:",
                "        original_data['datacleaning_method'] = next(iter(cleaning_settings.keys()), None)",
                "    normalization = MEDiml.learning.Normalization.CombatNormalization()",
                "    rad_tables_learning[index] = normalization.fit_transform(rad_table_learning)",
                "normalized_features = True",
            ],
        )

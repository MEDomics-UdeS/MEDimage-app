from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LearningContext:
    """Mutable execution state shared by the learning workflow."""

    pipeline_index: int = 0
    pipeline_name: str = ""
    pipeline_description: str = ""
    pipeline_ids: list[str] = field(default_factory=list)

    path_ws_experiments: Path | None = None
    path_settings: Path | None = None
    path_study: Path | None = None
    path_results: Path | None = None
    path_save_experiments: Path | None = None
    path_outcome_file: Path | None = None

    experiment_label: str | None = None
    outcome_name: str | None = None
    method: str | None = None
    design_settings: dict[str, Any] = field(default_factory=dict)
    split_settings: dict[str, Any] = field(default_factory=dict)
    data_settings: dict[str, Any] = field(default_factory=dict)
    cleaning_settings: dict[str, Any] = field(default_factory=dict)
    normalization_settings: dict[str, Any] = field(default_factory=dict)
    fsr_settings: dict[str, Any] = field(default_factory=dict)
    learner_settings: dict[str, Any] = field(default_factory=dict)
    analyze_settings: dict[str, Any] = field(default_factory=dict)

    holdout_test: bool = False
    evaluate_holdout: bool = False
    splitted_data: bool = False
    designed_experiment: bool = False
    loaded_data: bool = False
    cleaned_data: bool = False
    normalized_features: bool = False
    reduced_features: bool = False
    finalize_model: bool = False
    saved_results: bool = False

    split_counter: int = 0
    nb_split: int = 0

    paths_splits: list[Path] = field(default_factory=list)
    rad_tables_learning: list[Any] = field(default_factory=list)
    rad_tables_testing: list[Any] = field(default_factory=list)
    rad_tables_training: list[Any] = field(default_factory=list)
    rad_tables_final: list[Any] = field(default_factory=list)

    rad_var_struct: dict[str, Any] = field(default_factory=lambda: {"path": {}})
    all_patients: list[str] | None = None
    patients_final_train: list[str] | None = None
    patients_holdout: list[str] | None = None
    patient_ids: list[str] = field(default_factory=list)

    outcome_table_binary: Any = None
    outcome_table_binary_training: Any = None
    outcome_table_binary_final: Any = None
    outcome_table_binary_train: Any = None
    outcome_table_binary_test: Any = None
    outcome_table_binary_holdout: Any = None

    path_ml_dict: dict[str, Any] = field(default_factory=dict)
    ml_dict_paths: dict[str, Any] = field(default_factory=dict)

    results_avg: list[dict[str, Any]] = field(default_factory=list)
    analysis_dict: dict[str, Any] = field(default_factory=dict)
    figures_dict: dict[str, Any] = field(default_factory=dict)
    final_results: dict[str, Any] | None = None

    current_model_id: str | None = None
    current_model: Any = None
    current_result: Any = None

    extras: dict[str, Any] = field(default_factory=dict)

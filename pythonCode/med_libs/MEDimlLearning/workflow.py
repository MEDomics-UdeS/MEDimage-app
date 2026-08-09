from __future__ import annotations

from dataclasses import dataclass
import shutil
from pathlib import Path
from typing import Any

from .node import LearningNode
from .pipeline import LearningContext, Pipeline
from .utils import get_node_content


@dataclass
class WorkflowBuildResult:
    pipelines: list[Pipeline]
    warnings: list[str]


class LearningWorkflow:
    """Builds and executes learning pipelines from a drawflow scene."""

    def __init__(self, json_config: dict[str, Any]) -> None:
        self.json_config = json_config
        self._progress = {"currentLabel": "", "now": 0.0}

    def get_progress(self) -> dict[str, Any]:
        return self._progress

    def set_progress(self, now: int = -1, label: str = "same") -> None:
        if now == -1:
            now = self._progress["now"]
        if label == "same":
            label = self._progress["currentLabel"]
        self._progress = {"currentLabel": label, "now": now}

    def _build_pipeline(self, node_id: str, node_content: dict[str, Any], pip: list[str], json_scene: dict[str, Any], pips: list[list[str]]) -> list[str]:
        pip.append(node_id)
        outputs = node_content.get("outputs", {})
        if "output_1" not in outputs:
            pips.append(pip[:])
            return pip
        connections = outputs["output_1"].get("connections", [])
        if len(connections) == 1:
            out_node_id = connections[0]["node"]
            out_node_content = get_node_content(out_node_id, json_scene)
            return self._build_pipeline(out_node_id, out_node_content, pip, json_scene, pips)
        for connection in connections:
            out_node_id = connection["node"]
            out_node_content = get_node_content(out_node_id, json_scene)
            self._build_pipeline(out_node_id, out_node_content, pip[:], json_scene, pips)
        return pip

    def build_pipelines(self) -> list[Pipeline]:
        drawflow_scene = self.json_config["drawflow"]
        pips: list[list[str]] = []
        for module in drawflow_scene:
            for node_id in drawflow_scene[module]["data"]:
                node_content = drawflow_scene[module]["data"][node_id]
                if not node_content.get("inputs"):
                    self._build_pipeline(str(node_content["id"]), node_content, [], self.json_config, pips)

        pipelines: list[Pipeline] = []
        for index, pip in enumerate(pips, start=1):
            nodes = [LearningNode.create_node(get_node_content(node_id, self.json_config)) for node_id in pip]
            pipelines.append(Pipeline(nodes, index, "pip" + "/".join(pip), "pipeline" + str(index)))
        return pipelines

    def run_all(self) -> dict[str, Any]:
        pipelines = self.build_pipelines()
        results: list[dict[str, Any]] = []
        contexts = []

        for index, pipeline in enumerate(pipelines, start=1):
            context = pipeline.run(self.set_progress, pipeline_number=index)
            contexts.append(context)
            results.append(
                {
                    "pipeline": pipeline.pipeline_name,
                    "id": pipeline.id,
                }
            )

        return self._aggregate_results(results, contexts)

    def _aggregate_results(self, results: list[dict[str, Any]], contexts: list[LearningContext]) -> dict[str, Any]:
        experiments_labels: list[str] = []
        analyzed_context = None

        for context in contexts:
            if context.experiment_label and context.experiment_label not in experiments_labels:
                experiments_labels.append(context.experiment_label)
            if analyzed_context is None and context.analyze_settings:
                analyzed_context = context

        warnings: list[str] = []
        if experiments_labels:
            experiment_prefix = experiments_labels[0].split("_")[0]
            for label in experiments_labels:
                if label.split("_")[0] != experiment_prefix:
                    warnings.append(
                        f"To analyze experiments, labels must start with the same name! {experiment_prefix} != {label}"
                    )
                    break

        figures_dict: dict[str, Any] = {}
        results_avg: list[dict[str, Any]] = []

        if analyzed_context is not None and analyzed_context.current_result is not None and analyzed_context.path_study is not None:
            result = analyzed_context.current_result
            analyze_settings = analyzed_context.analyze_settings
            experiment = analyzed_context.experiment_label.split("_")[0] if analyzed_context.experiment_label else ""
            level = analyzed_context.experiment_label.split("_")[1] if analyzed_context.experiment_label and "_" in analyzed_context.experiment_label else ""
            modality = analyzed_context.experiment_label.split("_")[-1] if analyzed_context.experiment_label else ""

            if analyze_settings.get("heatmap"):
                heatmap_params = analyze_settings.get("heatmapParams")
                if heatmap_params is None:
                    warnings.append("Analyze: Heatmap parameters were not provided")
                else:
                    metric = heatmap_params.get("metric")
                    plot_p_values = heatmap_params.get("pValues")
                    p_value_test = heatmap_params.get("pValuesMethod")
                    title = heatmap_params.get("title")
                    extra_metrics = heatmap_params.get("extraMetrics")
                    stat_extra = extra_metrics.split(",") if extra_metrics else None

                    result.plot_heatmap(
                        Path(analyzed_context.path_study),
                        experiments_labels=experiments_labels,
                        metric=metric,
                        stat_extra=stat_extra,
                        title=title,
                        plot_p_values=plot_p_values,
                        p_value_test=p_value_test,
                        save=True,
                    )

                    path_image = Path(analyzed_context.path_study) / (f"{title}.png" if title else f"{metric}_heatmap.png")
                    public_root = Path.cwd().parent / "renderer" / "public" / "images" / "analyze"
                    public_root.mkdir(parents=True, exist_ok=True)
                    copied_path = public_root / f"{path_image.stem}_{analyzed_context.pipeline_name}.png"
                    if path_image.exists():
                        shutil.copy(path_image, copied_path)
                    figures_dict["heatmap"] = {"path": str(copied_path if copied_path.exists() else path_image).replace("\\", "/")}

                if analyze_settings.get("optimalLevel"):
                    metric = analyze_settings.get("heatmapParams", {}).get("metric")
                    p_value_test = analyze_settings.get("heatmapParams", {}).get("pValuesMethod")
                    optimal_levels = result.get_optimal_level(
                        Path(analyzed_context.path_study),
                        experiments_labels=experiments_labels,
                        metric=metric,
                        p_value_test=p_value_test,
                        nb_split=analyzed_context.nb_split,
                    )
                    figures_dict["optimal_level"] = {"name": optimal_levels}

                    if analyze_settings.get("tree"):
                        modalities = list({label.split("_")[-1] for label in experiments_labels})
                        tree_dict: dict[str, Any] = {}
                        for idx, optimal_level in enumerate(optimal_levels):
                            current_modality = modalities[idx] if idx < len(modalities) else modalities[0]
                            if "Text" in optimal_level:
                                result.plot_original_level_tree(
                                    Path(analyzed_context.path_study),
                                    experiment=experiment,
                                    level=optimal_level,
                                    modalities=[current_modality],
                                    figsize=(25, 10),
                                )
                                tree_path = Path(analyzed_context.path_study) / f"Original_level_{experiment}_{optimal_level}_{current_modality}_explanation_tree.png"
                            elif "LF" in optimal_level:
                                result.plot_lf_level_tree(
                                    Path(analyzed_context.path_study),
                                    experiment=experiment,
                                    level=optimal_level,
                                    modalities=[current_modality],
                                    figsize=(25, 10),
                                )
                                tree_path = Path(analyzed_context.path_study) / f"LF_level_{experiment}_{optimal_level}_{current_modality}_explanation_tree.png"
                            elif "TF" in optimal_level:
                                result.plot_tf_level_tree(
                                    Path(analyzed_context.path_study),
                                    experiment=experiment,
                                    level=optimal_level,
                                    modalities=[current_modality],
                                    figsize=(25, 10),
                                )
                                tree_path = Path(analyzed_context.path_study) / f"TF_level_{experiment}_{optimal_level}_{current_modality}_explanation_tree.png"
                            else:
                                continue

                            public_root = Path.cwd().parent / "renderer" / "public" / "images" / "analyze"
                            public_root.mkdir(parents=True, exist_ok=True)
                            copied_tree = public_root / f"{tree_path.stem}_{analyzed_context.pipeline_name}.png"
                            if tree_path.exists():
                                shutil.copy(tree_path, copied_tree)
                            tree_dict[optimal_level] = {"path": str(copied_tree if copied_tree.exists() else tree_path).replace("\\", "/")}

                        figures_dict.setdefault("optimal_level", {})["tree"] = tree_dict

        for context in contexts:
            if context.final_results:
                results_avg.append(
                    {
                        context.pipeline_description: {
                            context.experiment_label: context.final_results,
                            "analysis": context.analysis_dict,
                        }
                    }
                )

        return {
            "experiments": experiments_labels,
            "results_avg": results_avg,
            "figures": figures_dict,
            "pipelines": results,
            "warning": warnings[0] if warnings else None,
        }

"""Run S2S-FDD on CVACaseStudy MATLAB data sets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .data import CVACASE_ROOT, PROJECT_ROOT, cvacase_context
from .deepseek_client import DeepSeekAPIError, DeepSeekClient
from .knowledge import KnowledgeRetriever, load_knowledge_cases
from .reasoning import RuleBasedReasoner
from .reconstruction import StateMatrixReconstructor
from .report import build_report
from .semantics import describe_variables
from .types import TimeSeriesData
from .variable_selection import select_key_variables


def _loadmat(path: Path) -> dict[str, object]:
    try:
        from scipy.io import loadmat  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install scipy to read CVACaseStudy .mat files.") from exc
    return loadmat(path)


def _dataset_key(fault_case: int, set_name: str | None) -> str:
    if set_name:
        return set_name
    return f"Set{fault_case}_1"


def _series_from_matrix(matrix: np.ndarray, variables: list[str]) -> TimeSeriesData:
    return TimeSeriesData(
        variables=variables,
        values=matrix.astype(float).tolist(),
        timestamps=[str(index) for index in range(len(matrix))],
    )


def _output_dir(output_root: Path, fault_case: int, dataset: str) -> Path:
    return output_root / "cvacase" / f"fault{fault_case}" / dataset.lower()


def run_cvacase(
    fault_case: int,
    set_name: str | None = None,
    output_root: Path = PROJECT_ROOT / "outputs",
    n_states: int = 10,
    alpha: float = 3.0,
    window: int = 10,
    top_k: int = 6,
    variance_multiplier: float = 1.1,
    llm_semantics: bool = False,
    semantic_model: str | None = None,
) -> dict[str, object]:
    """Run the current S2S-FDD scaffold on one CVACaseStudy faulty data set."""

    dataset = _dataset_key(fault_case, set_name)
    variable_count = 24 if fault_case == 6 else 23
    variables = [f"x{i}" for i in range(1, variable_count + 1)]

    training = _loadmat(CVACASE_ROOT / "Training.mat")
    faulty = _loadmat(CVACASE_ROOT / f"FaultyCase{fault_case}.mat")
    if dataset not in faulty:
        available = sorted(key for key in faulty if key.startswith(f"Set{fault_case}_"))
        raise ValueError(f"{dataset!r} not found. Available data sets: {', '.join(available)}")

    normal_matrix = np.vstack(
        [
            np.asarray(training["T2"])[:, :variable_count],
            np.asarray(training["T3"])[:, :variable_count],
        ]
    )
    fault_matrix = np.asarray(faulty[dataset])[:, :variable_count]
    normal = _series_from_matrix(normal_matrix, variables)
    fault = _series_from_matrix(fault_matrix, variables)

    context = cvacase_context()
    reconstructor = StateMatrixReconstructor(n_states=n_states).fit(normal)
    baseline = reconstructor.reconstruct(normal)
    fault_rec = reconstructor.reconstruct(fault)
    findings = select_key_variables(
        normal=normal,
        baseline_reconstruction=baseline,
        fault_reconstruction=fault_rec,
        alpha=alpha,
        window=window,
        top_score=top_k,
        top_early=top_k,
        variance_multiplier=variance_multiplier,
    )

    semantic_generator = None
    semantic_source = "local"
    if llm_semantics:
        semantic_generator = DeepSeekClient(model=semantic_model).generate_semantic_description
        semantic_source = "deepseek"
    descriptions = describe_variables(
        context,
        fault_rec,
        findings,
        text_generator=semantic_generator,
    )

    cases = load_knowledge_cases(context.fault_knowledge_path)
    retrieved = KnowledgeRetriever(cases).retrieve(descriptions, top_k=top_k)
    diagnosis = RuleBasedReasoner().diagnose(context, descriptions, retrieved)
    report = build_report(findings, descriptions, retrieved, diagnosis)
    report["dataset"] = {
        "normal": f"T2+T3 first {variable_count} variables",
        "fault": f"FaultyCase{fault_case} {dataset} first {variable_count} variables",
        "expected_fault": f"Fault Case {fault_case}",
        "n_states": n_states,
        "alpha": alpha,
        "window": window,
        "semantic_source": semantic_source,
    }

    destination = _output_dir(output_root, fault_case, dataset)
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / f"report_{semantic_source}.json"
    semantic_path = destination / f"semantic_descriptions_{semantic_source}.json"
    report["output_paths"] = {
        "report": str(report_path),
        "semantic_descriptions": str(semantic_path),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    semantic_path.write_text(
        json.dumps(
            [{"variable": item.variable, "text": item.text} for item in descriptions],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run S2S-FDD on CVACaseStudy .mat data.")
    parser.add_argument("--fault-case", type=int, default=1)
    parser.add_argument("--set", dest="set_name", default=None, help="Data set key, e.g. Set1_1.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "outputs")
    parser.add_argument("--n-states", type=int, default=10)
    parser.add_argument("--alpha", type=float, default=3.0)
    parser.add_argument("--window", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--variance-multiplier", type=float, default=1.1)
    parser.add_argument("--llm-semantics", action="store_true")
    parser.add_argument("--semantic-model", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        report = run_cvacase(
            fault_case=args.fault_case,
            set_name=args.set_name,
            output_root=args.output_root,
            n_states=args.n_states,
            alpha=args.alpha,
            window=args.window,
            top_k=args.top_k,
            variance_multiplier=args.variance_multiplier,
            llm_semantics=args.llm_semantics,
            semantic_model=args.semantic_model,
        )
    except DeepSeekAPIError as exc:
        raise SystemExit(f"DeepSeek semantic generation failed: {exc}") from exc

    print(report["summary"])
    diagnosis = report.get("diagnosis", {})
    if isinstance(diagnosis, dict):
        print(f"Diagnosis: {diagnosis.get('answer') or 'not determined'}")
    output_paths = report.get("output_paths", {})
    if isinstance(output_paths, dict):
        print(f"Report written to {output_paths.get('report')}")
        print(f"Semantic descriptions written to {output_paths.get('semantic_descriptions')}")


if __name__ == "__main__":
    main()

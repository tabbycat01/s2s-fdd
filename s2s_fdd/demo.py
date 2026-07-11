"""Run a minimal end-to-end S2S-FDD pipeline."""

from __future__ import annotations

import os
import sys

if __package__ in {None, ""}:
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(package_dir)
    sys.path = [path for path in sys.path if os.path.abspath(path or os.curdir) != package_dir]
    sys.path.insert(0, project_root)
    __package__ = "s2s_fdd"

import argparse
import json
from pathlib import Path

from .data import PROJECT_ROOT, demo_context, ensure_same_variables, read_timeseries_csv
from .knowledge import KnowledgeRetriever, load_knowledge_cases
from .deepseek_client import DeepSeekAPIError, DeepSeekClient
from .reasoning import RuleBasedReasoner
from .reconstruction import StateMatrixReconstructor
from .report import build_report
from .semantics import describe_variables
from .variable_selection import select_key_variables


def run_demo(
    normal_file: Path,
    fault_file: Path,
    n_states: int = 16,
    alpha: float = 3.0,
    window: int = 3,
    top_k: int = 3,
    knowledge_path: Path | None = None,
    llm_semantics: bool = False,
    semantic_model: str | None = None,
) -> dict[str, object]:
    normal = read_timeseries_csv(normal_file)
    fault = read_timeseries_csv(fault_file)
    ensure_same_variables(normal, fault)

    context = demo_context(normal.variables)
    reconstructor = StateMatrixReconstructor(n_states=n_states).fit(normal)
    baseline_reconstruction = reconstructor.reconstruct(normal)
    fault_reconstruction = reconstructor.reconstruct(fault)

    findings = select_key_variables(
        normal=normal,
        baseline_reconstruction=baseline_reconstruction,
        fault_reconstruction=fault_reconstruction,
        alpha=alpha,
        window=window,
        top_score=top_k,
        top_early=top_k,
    )
    semantic_generator = None
    if llm_semantics:
        semantic_generator = DeepSeekClient(model=semantic_model).generate_semantic_description
    descriptions = describe_variables(
        context,
        fault_reconstruction,
        findings,
        text_generator=semantic_generator,
    )
    cases = load_knowledge_cases(knowledge_path or context.fault_knowledge_path)
    retrieved = KnowledgeRetriever(cases).retrieve(descriptions, top_k=top_k)
    diagnosis = RuleBasedReasoner().diagnose(context, descriptions, retrieved)

    return build_report(
        findings=findings,
        descriptions=descriptions,
        retrieved=retrieved,
        diagnosis=diagnosis,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the S2S-FDD scaffold demo.")
    parser.add_argument("--normal", type=Path, default=PROJECT_ROOT / "examples" / "normal.csv")
    parser.add_argument("--fault", type=Path, default=PROJECT_ROOT / "examples" / "fault.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "outputs" / "demo_result.json")
    parser.add_argument("--knowledge", type=Path, default=None)
    parser.add_argument("--n-states", type=int, default=16)
    parser.add_argument("--alpha", type=float, default=3.0)
    parser.add_argument("--window", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--llm-semantics",
        action="store_true",
        help="Generate temporal semantic descriptions with the DeepSeek API.",
    )
    parser.add_argument(
        "--semantic-model",
        default=None,
        help="DeepSeek model for --llm-semantics. Defaults to DEEPSEEK_MODEL or the project default.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = run_demo(
            normal_file=args.normal,
            fault_file=args.fault,
            n_states=args.n_states,
            alpha=args.alpha,
            window=args.window,
            top_k=args.top_k,
            knowledge_path=args.knowledge,
            llm_semantics=args.llm_semantics,
            semantic_model=args.semantic_model,
        )
    except DeepSeekAPIError as exc:
        raise SystemExit(f"DeepSeek semantic generation failed: {exc}") from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(result["summary"])
    diagnosis = result["diagnosis"]
    if isinstance(diagnosis, dict):
        print(f"Diagnosis: {diagnosis.get('answer') or 'not determined'}")
    print(f"Structured result written to {args.output}")


if __name__ == "__main__":
    main()

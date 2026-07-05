"""Diagnostic report assembly."""

from __future__ import annotations

from dataclasses import asdict

from .types import DiagnosisResult, RetrievedCase, SemanticDescription, VariableFinding


def summarize_findings(findings: list[VariableFinding]) -> str:
    if not findings:
        return "No key abnormal variables were selected."
    names = ", ".join(item.variable for item in findings)
    leading = findings[0]
    return (
        f"Selected {len(findings)} key variables: {names}. "
        f"Strongest variable: {leading.variable}, score {leading.score:.2f}."
    )


def build_report(
    findings: list[VariableFinding],
    descriptions: list[SemanticDescription],
    retrieved: list[RetrievedCase],
    diagnosis: DiagnosisResult,
) -> dict[str, object]:
    return {
        "summary": summarize_findings(findings),
        "key_variables": [asdict(item) for item in findings],
        "semantic_descriptions": [
            {"variable": item.variable, "text": item.text, "table_rows": len(item.table)}
            for item in descriptions
        ],
        "retrieved_cases": [
            {"case_id": item.case.case_id, "title": item.case.title, "score": item.score}
            for item in retrieved
        ],
        "diagnosis": asdict(diagnosis),
    }

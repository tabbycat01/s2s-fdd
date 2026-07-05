"""Diagnostic reasoning orchestration and tool-call parsing."""

from __future__ import annotations

import re

from .semantics import build_target_table
from .types import (
    DiagnosisResult,
    ProcessContext,
    ReconstructionResult,
    RetrievedCase,
    SemanticDescription,
    VariableFinding,
)


TAG_RE = re.compile(r"<(?P<tag>answer|reasoning|tool|uncertain)>(?P<body>.*?)</(?P=tag)>", re.S)
TOOL_RE = re.compile(r"get_target_table\s*\(\s*[\"'](?P<sensor>[^\"']+)[\"']\s*\)")


def build_diagnosis_prompt(
    context: ProcessContext,
    descriptions: list[SemanticDescription],
    retrieved: list[RetrievedCase],
) -> str:
    knowledge = "\n\n".join(
        f"[{item.case.case_id}] {item.case.title}\n{item.matched_chunk[:1200]}"
        for item in retrieved
    ) or "No external fault knowledge was retrieved."
    observations = "\n".join(f"- {item.variable}: {item.text}" for item in descriptions)
    return f"""You are an industrial fault diagnosis expert.

Process:
{context.process_info}

Sensors:
{context.sensor_text()}

Fault knowledge:
{knowledge}

Time-series observations:
{observations}

Return one of these formats:
<reasoning>step-by-step diagnosis</reasoning><answer>fault id or name</answer>
<reasoning>why more data is needed</reasoning><tool>get_target_table("SENSOR")</tool>
<reasoning>why the case is ambiguous</reasoning><uncertain>candidate faults</uncertain>"""


def parse_model_response(text: str) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {"answer": [], "reasoning": [], "tool": [], "uncertain": []}
    for match in TAG_RE.finditer(text):
        parsed[match.group("tag")].append(match.group("body").strip())
    return parsed


def get_target_table(
    sensor: str,
    reconstruction: ReconstructionResult,
    findings: list[VariableFinding],
) -> list[dict[str, float | str]]:
    finding = next((item for item in findings if item.variable == sensor), None)
    if finding is None:
        raise ValueError(f"{sensor!r} is not a selected key variable.")
    return build_target_table(reconstruction, finding)


class RuleBasedReasoner:
    """Deterministic fallback reasoner used before wiring a live LLM."""

    def diagnose(
        self,
        context: ProcessContext,
        descriptions: list[SemanticDescription],
        retrieved: list[RetrievedCase],
    ) -> DiagnosisResult:
        prompt = build_diagnosis_prompt(context, descriptions, retrieved)
        if retrieved:
            answer = retrieved[0].case.title
            reasoning = (
                "The top retrieved fault case has the highest lexical match to the "
                "generated temporal descriptions. A live LLM should replace this "
                "fallback for final root-cause reasoning."
            )
        else:
            answer = None
            reasoning = (
                "No fault knowledge was available, so the pipeline can only report "
                "key abnormal variables and semantic evidence."
            )
        return DiagnosisResult(
            answer=answer,
            reasoning=reasoning,
            uncertain=[] if answer else [description.variable for description in descriptions],
            tool_calls=[],
            messages=[prompt, reasoning],
        )

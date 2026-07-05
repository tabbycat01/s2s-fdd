"""Temporal semantic prompt construction and local summarization."""

from __future__ import annotations

from statistics import mean

from .types import ProcessContext, ReconstructionResult, SemanticDescription, VariableFinding


SEMANTIC_BANK = """Global layer: trend, range, mean, extrema, volatility.
Stage layer: early/middle/late behavior and phase boundaries.
Event layer: turning points, jumps, sharp drops, repeated cycles, anomaly onset order."""


def build_target_table(
    reconstruction: ReconstructionResult,
    finding: VariableFinding,
    max_rows: int = 80,
) -> list[dict[str, float | str]]:
    index = reconstruction.variables.index(finding.variable)
    table: list[dict[str, float | str]] = []
    stride = max(1, len(reconstruction.timestamps) // max_rows)
    for row_index in range(0, len(reconstruction.timestamps), stride):
        observed = reconstruction.observed[row_index][index]
        expected = reconstruction.reconstructed[row_index][index]
        residual = reconstruction.residuals[row_index][index]
        percent = residual / max(abs(expected), 1e-9) * 100.0
        table.append(
            {
                "timestamp": reconstruction.timestamps[row_index],
                "observed": round(observed, 6),
                "expected": round(expected, 6),
                "residual": round(residual, 6),
                "residual_percent": round(percent, 3),
            }
        )
    return table


def build_semantic_prompt(
    context: ProcessContext,
    finding: VariableFinding,
    table: list[dict[str, float | str]],
) -> str:
    return f"""Your task is to describe the deviation of one sensor from its ideal reconstructed value.

Process information:
{context.process_info}

All sensors:
{context.sensor_text()}

Target sensor: {finding.variable}

Temporal analytic semantic bank:
{SEMANTIC_BANK}

Data table:
{table}

Focus on periods where residuals exceed the normal range. Describe observable trend, whether measured values are above or below reconstructed values, and key intervals. Avoid root-cause claims."""


def local_semantic_summary(
    reconstruction: ReconstructionResult,
    finding: VariableFinding,
) -> str:
    index = reconstruction.variables.index(finding.variable)
    residuals = [row[index] for row in reconstruction.residuals]
    observed = [row[index] for row in reconstruction.observed]
    midpoint = max(1, len(observed) // 2)
    early = mean(observed[:midpoint])
    late = mean(observed[midpoint:])
    trend = "rises" if late > early else "falls" if late < early else "stays nearly flat"
    direction = "above" if mean(residuals) > 0 else "below"
    first = finding.first_anomaly_time or "not confirmed by a continuous window"
    return (
        f"{finding.variable} {trend} during the observed interval and is mostly {direction} "
        f"the reconstructed normal value. First continuous anomaly time: {first}. "
        f"Max residual {finding.max_residual:.3f}, anomaly ratio {finding.anomaly_ratio:.0%}."
    )


def describe_variables(
    context: ProcessContext,
    reconstruction: ReconstructionResult,
    findings: list[VariableFinding],
) -> list[SemanticDescription]:
    descriptions: list[SemanticDescription] = []
    for finding in findings:
        table = build_target_table(reconstruction, finding)
        prompt = build_semantic_prompt(context, finding, table)
        descriptions.append(
            SemanticDescription(
                variable=finding.variable,
                text=local_semantic_summary(reconstruction, finding),
                prompt=prompt,
                table=table,
            )
        )
    return descriptions

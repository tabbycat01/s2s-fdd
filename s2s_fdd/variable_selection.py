"""Key-variable selection following the S2S-FDD paper."""

from __future__ import annotations

import numpy as np

from .types import ReconstructionResult, TimeSeriesData, VariableFinding


EPSILON = 1e-9


def _first_continuous_time(flags: np.ndarray, timestamps: list[str], window: int) -> str | None:
    if window <= 1:
        indexes = np.where(flags)[0]
        return timestamps[int(indexes[0])] if len(indexes) else None

    for start in range(0, len(flags) - window + 1):
        if bool(flags[start : start + window].all()):
            return timestamps[start]
    return None


def select_key_variables(
    normal: TimeSeriesData,
    baseline_reconstruction: ReconstructionResult,
    fault_reconstruction: ReconstructionResult,
    alpha: float = 3.0,
    window: int = 5,
    top_score: int = 5,
    top_early: int = 5,
    variance_multiplier: float = 2.0,
) -> list[VariableFinding]:
    """Select variables with large residuals, early onset, and variance change."""

    baseline_abs = np.abs(np.asarray(baseline_reconstruction.residuals, dtype=float))
    fault_abs = np.abs(np.asarray(fault_reconstruction.residuals, dtype=float))
    normal_values = np.asarray(normal.values, dtype=float)
    fault_values = np.asarray(fault_reconstruction.observed, dtype=float)

    findings: list[VariableFinding] = []
    for index, variable in enumerate(fault_reconstruction.variables):
        baseline_error = float(max(baseline_abs[:, index].mean(), EPSILON))
        threshold = alpha * baseline_error
        residuals = fault_abs[:, index]
        flags = residuals >= threshold
        exceed = residuals[flags]
        score = float(((exceed.mean() / baseline_error) - 1.0) * 100.0) if len(exceed) else 0.0
        first_time = _first_continuous_time(flags, fault_reconstruction.timestamps, window)
        variance_ratio = float(
            np.var(fault_values[:, index]) / max(np.var(normal_values[:, index]), EPSILON)
        )
        findings.append(
            VariableFinding(
                variable=variable,
                score=score,
                baseline_error=baseline_error,
                threshold=float(threshold),
                first_anomaly_time=first_time,
                anomaly_ratio=float(flags.mean()),
                max_residual=float(residuals.max()),
                mean_residual=float(residuals.mean()),
                variance_ratio=variance_ratio,
            )
        )

    by_score = sorted(findings, key=lambda item: item.score, reverse=True)[:top_score]
    by_early = sorted(
        [item for item in findings if item.first_anomaly_time is not None],
        key=lambda item: fault_reconstruction.timestamps.index(item.first_anomaly_time or ""),
    )[:top_early]
    selected = {item.variable: item for item in by_score + by_early}
    filtered = [
        item for item in selected.values() if item.variance_ratio >= variance_multiplier or item.score > 0
    ]
    return sorted(filtered, key=lambda item: (item.score, item.max_residual), reverse=True)

"""Temporal semantic prompt construction and local summarization."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from statistics import mean, pstdev

from .types import ProcessContext, ReconstructionResult, SemanticDescription, VariableFinding


SEMANTIC_BANK = """Global layer: trend, mean shift, extrema, overall volatility, and direction against the ideal normal value.
Stage layer: early/middle/late behavior, anomaly start time, persistent intervals, and recovery.
Event layer: significant exceedance, sudden rise, sudden drop, turning point, periodic fluctuation, residual sign change, and key abnormal intervals.
CVA evidence layer: describe when the variable deviates significantly as if reading T2/Q indicators and contribution plots, but do not infer the fault root cause."""


@dataclass(frozen=True)
class StageSummary:
    name: str
    start_time: str
    end_time: str
    observed_mean: float
    residual_mean: float
    residual_max: float
    threshold_exceed_ratio: float
    direction: str
    trend: str


@dataclass(frozen=True)
class TemporalFeatures:
    variable: str
    sensor_label: str
    threshold: float
    global_trend: str
    residual_direction: str
    residual_mean: float
    residual_max: float
    residual_std: float
    anomaly_ratio: float
    first_anomaly_time: str | None
    peak_time: str
    sign_changes: int
    sharp_events: list[str]
    abnormal_intervals: list[tuple[str, str]]
    stages: list[StageSummary]


def _sensor_label(context: ProcessContext, variable: str) -> str:
    sensor = next((item for item in context.sensors if item.name == variable), None)
    if sensor is None:
        return variable
    detail = sensor.description or sensor.name
    unit = f", unit={sensor.unit}" if sensor.unit else ""
    return f"{sensor.name} ({detail}{unit})"


def _trend(values: list[float], tolerance: float | None = None) -> str:
    if len(values) < 2:
        return "stable"
    delta = values[-1] - values[0]
    spread = max(values) - min(values)
    limit = tolerance if tolerance is not None else max(spread * 0.05, 1e-9)
    if delta > limit:
        return "rising"
    if delta < -limit:
        return "falling"
    return "stable"


def _direction(value: float) -> str:
    if value > 0:
        return "above the ideal normal value"
    if value < 0:
        return "below the ideal normal value"
    return "near the ideal normal value"


def _abnormal_intervals(flags: list[bool], timestamps: list[str]) -> list[tuple[str, str]]:
    intervals: list[tuple[str, str]] = []
    start: int | None = None
    for index, flag in enumerate(flags):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            intervals.append((timestamps[start], timestamps[index - 1]))
            start = None
    if start is not None:
        intervals.append((timestamps[start], timestamps[-1]))
    return intervals


def _sign_changes(values: list[float]) -> int:
    signs: list[int] = []
    for value in values:
        if value > 0:
            signs.append(1)
        elif value < 0:
            signs.append(-1)
        else:
            signs.append(0)
    return sum(1 for left, right in zip(signs, signs[1:]) if left and right and left != right)


def _sharp_events(values: list[float], timestamps: list[str], max_events: int = 5) -> list[str]:
    if len(values) < 3:
        return []
    deltas = [abs(right - left) for left, right in zip(values, values[1:])]
    cutoff = mean(deltas) + 2.0 * (pstdev(deltas) if len(deltas) > 1 else 0.0)
    events = [
        f"{timestamps[index + 1]}: delta={values[index + 1] - values[index]:.6g}"
        for index, delta in enumerate(deltas)
        if delta >= cutoff and delta > 0
    ]
    return events[:max_events]


def _slice_stage(
    name: str,
    start: int,
    end: int,
    timestamps: list[str],
    observed: list[float],
    residuals: list[float],
    abs_residuals: list[float],
    threshold: float,
) -> StageSummary:
    stage_observed = observed[start:end]
    stage_residuals = residuals[start:end]
    stage_abs = abs_residuals[start:end]
    if not stage_observed:
        stage_observed = [observed[-1]]
        stage_residuals = [residuals[-1]]
        stage_abs = [abs_residuals[-1]]
        start = end = len(observed) - 1
    exceed_ratio = sum(value >= threshold for value in stage_abs) / max(len(stage_abs), 1)
    residual_mean = mean(stage_residuals)
    return StageSummary(
        name=name,
        start_time=timestamps[start],
        end_time=timestamps[max(start, end - 1)],
        observed_mean=mean(stage_observed),
        residual_mean=residual_mean,
        residual_max=max(stage_abs),
        threshold_exceed_ratio=exceed_ratio,
        direction=_direction(residual_mean),
        trend=_trend(stage_observed),
    )


def extract_temporal_features(
    context: ProcessContext,
    reconstruction: ReconstructionResult,
    finding: VariableFinding,
) -> TemporalFeatures:
    index = reconstruction.variables.index(finding.variable)
    observed = [row[index] for row in reconstruction.observed]
    residuals = [row[index] for row in reconstruction.residuals]
    abs_residuals = [abs(value) for value in residuals]
    flags = [value >= finding.threshold for value in abs_residuals]
    peak_index = max(range(len(abs_residuals)), key=lambda item: abs_residuals[item])
    count = len(observed)
    cuts = [0, count // 3, (2 * count) // 3, count]
    stages = [
        _slice_stage("early", cuts[0], cuts[1], reconstruction.timestamps, observed, residuals, abs_residuals, finding.threshold),
        _slice_stage("middle", cuts[1], cuts[2], reconstruction.timestamps, observed, residuals, abs_residuals, finding.threshold),
        _slice_stage("late", cuts[2], cuts[3], reconstruction.timestamps, observed, residuals, abs_residuals, finding.threshold),
    ]
    residual_mean = mean(residuals)
    return TemporalFeatures(
        variable=finding.variable,
        sensor_label=_sensor_label(context, finding.variable),
        threshold=finding.threshold,
        global_trend=_trend(observed),
        residual_direction=_direction(residual_mean),
        residual_mean=residual_mean,
        residual_max=max(abs_residuals),
        residual_std=pstdev(residuals) if len(residuals) > 1 else 0.0,
        anomaly_ratio=sum(flags) / max(len(flags), 1),
        first_anomaly_time=finding.first_anomaly_time,
        peak_time=reconstruction.timestamps[peak_index],
        sign_changes=_sign_changes(residuals),
        sharp_events=_sharp_events(residuals, reconstruction.timestamps),
        abnormal_intervals=_abnormal_intervals(flags, reconstruction.timestamps),
        stages=stages,
    )


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
                "abs_residual": round(abs(residual), 6),
                "residual_percent": round(percent, 3),
                "normal_mean_abs_deviation": round(finding.baseline_error, 6),
                "normal_mean_abs_deviation_percent": round(
                    finding.baseline_error / max(abs(expected), 1e-9) * 100.0,
                    3,
                ),
                "threshold": round(finding.threshold, 6),
                "exceeds_threshold": "yes" if abs(residual) >= finding.threshold else "no",
            }
        )
    return table


def _format_features(features: TemporalFeatures) -> str:
    intervals = (
        ", ".join(f"{start} to {end}" for start, end in features.abnormal_intervals[:6])
        or "no significant exceedance interval"
    )
    sharp = "; ".join(features.sharp_events) or "no obvious sharp event detected"
    stage_lines = "\n".join(
        (
            f"- {stage.name} ({stage.start_time} to {stage.end_time}): "
            f"{stage.trend}, {stage.direction}, residual_mean={stage.residual_mean:.6g}, "
            f"max_abs_residual={stage.residual_max:.6g}, "
            f"exceed_ratio={stage.threshold_exceed_ratio:.1%}"
        )
        for stage in features.stages
    )
    return f"""Target sensor: {features.sensor_label}
Significant deviation threshold: {features.threshold:.6g}
Global trend: {features.global_trend}
Mean residual direction: {features.residual_direction}
Mean residual: {features.residual_mean:.6g}
Maximum absolute residual: {features.residual_max:.6g}, time: {features.peak_time}
Residual standard deviation: {features.residual_std:.6g}
Anomaly ratio: {features.anomaly_ratio:.1%}
First continuous anomaly time: {features.first_anomaly_time or "not confirmed"}
Residual sign changes: {features.sign_changes}
Significant abnormal intervals: {intervals}
Sharp events: {sharp}
Stage summaries:
{stage_lines}"""


def build_semantic_prompt(
    context: ProcessContext,
    finding: VariableFinding,
    table: list[dict[str, float | str]],
    features: TemporalFeatures | None = None,
) -> str:
    feature_text = _format_features(features) if features is not None else "Temporal evidence was not precomputed."
    return f"""Your task is to describe the deviation between one measurement point and its ideal normal value, focusing on trend, periodic pattern, volatility, and key abnormal conditions from the temporal semantic bank.

Background information:
Process information: {context.process_info}
All sensors:
{context.sensor_text()}
Target sensor: {finding.variable}
Temporal semantic bank:
{SEMANTIC_BANK}
Precomputed temporal evidence:
{feature_text}
Data table:
{table}

The data table includes observed measurement observed, ideal normal value expected, deviation residual, time-varying deviation percentage residual_percent, normal mean absolute deviation normal_mean_abs_deviation, normal mean absolute deviation percentage normal_mean_abs_deviation_percent, and whether the deviation at that time significantly exceeds the normal range exceeds_threshold.

Only focus on periods where the deviation or deviation percentage significantly exceeds the normal range, because these periods may indicate a fault. Ignore periods where the deviation or percentage is close to normal operating conditions.

Within these significant deviation periods, describe two points:
1. The measurement trend, including rising, falling, stable, or periodic fluctuation.
2. Whether the measurement is above or below the ideal value.

If the deviation is not significant over the whole period, state that the variable has no obvious anomaly. Provide quantitative indicators, such as time interval, first anomaly time, maximum deviation time, or anomaly ratio, and qualitative insight describing how the measurement changes during significant deviation periods. Focus on observable patterns and avoid speculation or conclusions about the fault root cause. Do not use subtitles or Markdown syntax. Keep the answer concise, within 100 words."""


def local_semantic_summary(
    context: ProcessContext,
    reconstruction: ReconstructionResult,
    finding: VariableFinding,
) -> str:
    features = extract_temporal_features(context, reconstruction, finding)
    intervals = (
        ", ".join(f"{start}-{end}" for start, end in features.abnormal_intervals[:3])
        or "no continuous significant abnormal interval"
    )
    strongest_stage = max(features.stages, key=lambda stage: stage.residual_max)
    oscillation = (
        " Repeated residual sign changes suggest periodic or oscillatory fluctuation."
        if features.sign_changes >= 4
        else ""
    )
    first = features.first_anomaly_time or "not confirmed by a continuous window"
    return (
        f"{features.sensor_label} is generally {features.global_trend} and mostly "
        f"{features.residual_direction}. First continuous anomaly time: {first}. "
        f"Maximum absolute residual {features.residual_max:.3f} occurs at {features.peak_time}; "
        f"anomaly ratio is {features.anomaly_ratio:.0%}. The strongest deviation stage is "
        f"{strongest_stage.name} ({strongest_stage.start_time}-{strongest_stage.end_time}), "
        f"with significant abnormal intervals: {intervals}."
        f"{oscillation}"
    )


def describe_variables(
    context: ProcessContext,
    reconstruction: ReconstructionResult,
    findings: list[VariableFinding],
    text_generator: Callable[[str], str] | None = None,
) -> list[SemanticDescription]:
    descriptions: list[SemanticDescription] = []
    for finding in findings:
        table = build_target_table(reconstruction, finding)
        features = extract_temporal_features(context, reconstruction, finding)
        prompt = build_semantic_prompt(context, finding, table, features)
        text = text_generator(prompt) if text_generator is not None else local_semantic_summary(
            context, reconstruction, finding
        )
        descriptions.append(
            SemanticDescription(
                variable=finding.variable,
                text=text,
                prompt=prompt,
                table=table,
            )
        )
    return descriptions

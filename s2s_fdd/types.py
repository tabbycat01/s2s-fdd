"""Shared data structures for the S2S-FDD pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SensorMeta:
    """Human-readable metadata for one process variable."""

    name: str
    description: str = ""
    unit: str = ""


@dataclass(frozen=True)
class ProcessContext:
    """Static context injected into semantic and diagnostic prompts."""

    name: str
    process_info: str
    sensors: list[SensorMeta]
    fault_knowledge_path: Path | None = None

    @property
    def sensor_names(self) -> list[str]:
        return [sensor.name for sensor in self.sensors]

    def sensor_text(self) -> str:
        parts: list[str] = []
        for sensor in self.sensors:
            detail = sensor.description or "no description"
            unit = f", unit: {sensor.unit}" if sensor.unit else ""
            parts.append(f"- {sensor.name}: {detail}{unit}")
        return "\n".join(parts)


@dataclass(frozen=True)
class TimeSeriesData:
    """A dense time-series matrix with row-wise timestamps."""

    variables: list[str]
    values: list[list[float]]
    timestamps: list[str]

    def column(self, variable: str) -> list[float]:
        index = self.variables.index(variable)
        return [row[index] for row in self.values]


@dataclass(frozen=True)
class ReconstructionResult:
    variables: list[str]
    timestamps: list[str]
    observed: list[list[float]]
    reconstructed: list[list[float]]
    residuals: list[list[float]]


@dataclass(frozen=True)
class VariableFinding:
    variable: str
    score: float
    baseline_error: float
    threshold: float
    first_anomaly_time: str | None
    anomaly_ratio: float
    max_residual: float
    mean_residual: float
    variance_ratio: float


@dataclass(frozen=True)
class SemanticDescription:
    variable: str
    text: str
    prompt: str
    table: list[dict[str, float | str]]


@dataclass(frozen=True)
class KnowledgeCase:
    case_id: str
    title: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedCase:
    case: KnowledgeCase
    score: float
    matched_chunk: str


@dataclass(frozen=True)
class DiagnosisResult:
    answer: str | None
    reasoning: str
    uncertain: list[str]
    tool_calls: list[str]
    messages: list[str]

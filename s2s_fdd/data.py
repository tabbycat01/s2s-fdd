"""Data loading and built-in process contexts."""

from __future__ import annotations

import csv
from pathlib import Path

from .types import ProcessContext, SensorMeta, TimeSeriesData


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CVACASE_ROOT = PROJECT_ROOT / "CVACaseStudy" / "CVACaseStudy"


def read_timeseries_csv(path: Path) -> TimeSeriesData:
    """Read a CSV file with a timestamp column and numeric sensor columns."""

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "timestamp" not in reader.fieldnames:
            raise ValueError(f"{path} must contain a timestamp column.")

        variables = [name for name in reader.fieldnames if name != "timestamp"]
        timestamps: list[str] = []
        values: list[list[float]] = []

        for index, raw_row in enumerate(reader, start=2):
            timestamps.append(raw_row["timestamp"])
            row: list[float] = []
            for variable in variables:
                try:
                    row.append(float(raw_row[variable]))
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"{path}:{index} has a non-numeric value for {variable!r}."
                    ) from exc
            values.append(row)

    if not values:
        raise ValueError(f"{path} contains no data rows.")
    return TimeSeriesData(variables=variables, values=values, timestamps=timestamps)


def load_mat_timeseries(path: Path, variable_name: str | None = None) -> TimeSeriesData:
    """Load a MATLAB matrix as time-series data when scipy is available.

    CVACaseStudy ships MATLAB ``.mat`` files. This helper keeps scipy optional so
    the light CSV demo still runs on a fresh Python install.
    """

    try:
        from scipy.io import loadmat  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install scipy to read CVACaseStudy .mat files.") from exc

    content = loadmat(path)
    candidates = {
        key: value
        for key, value in content.items()
        if not key.startswith("__") and getattr(value, "ndim", 0) == 2
    }
    if not candidates:
        raise ValueError(f"{path} does not contain a 2-D matrix.")

    key = variable_name or max(candidates, key=lambda item: candidates[item].size)
    matrix = candidates[key]
    variables = [f"x{i + 1}" for i in range(matrix.shape[1])]
    timestamps = [str(i) for i in range(matrix.shape[0])]
    return TimeSeriesData(
        variables=variables,
        values=matrix.astype(float).tolist(),
        timestamps=timestamps,
    )


def ensure_same_variables(normal: TimeSeriesData, observed: TimeSeriesData) -> None:
    if normal.variables != observed.variables:
        raise ValueError("Normal and observed data must contain the same variables.")


def demo_context(variables: list[str]) -> ProcessContext:
    sensors = [SensorMeta(name=variable, description="demo process measurement") for variable in variables]
    return ProcessContext(
        name="CSV demo process",
        process_info=(
            "A minimal industrial process example used to exercise the S2S-FDD "
            "pipeline before connecting a domain-specific dataset."
        ),
        sensors=sensors,
    )


def cvacase_context() -> ProcessContext:
    sensors = [
        SensorMeta(name=f"x{i}", description="CVACaseStudy process variable")
        for i in range(1, 24)
    ]
    return ProcessContext(
        name="CVACaseStudy",
        process_info=(
            "CVACaseStudy is a canonical variate analysis process monitoring "
            "benchmark containing normal training data and multiple faulty cases."
        ),
        sensors=sensors,
        fault_knowledge_path=CVACASE_ROOT / "html" / "CUBenchmark.html",
    )

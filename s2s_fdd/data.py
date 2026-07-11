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
        SensorMeta(name="x1", description="PT312 air delivery pressure", unit="MPa"),
        SensorMeta(name="x2", description="PT401 pressure at bottom of riser", unit="MPa"),
        SensorMeta(name="x3", description="PT408 pressure at top of riser", unit="MPa"),
        SensorMeta(name="x4", description="PT403 pressure in top separator", unit="MPa"),
        SensorMeta(name="x5", description="PT501 pressure in three-phase separator", unit="MPa"),
        SensorMeta(name="x6", description="Differential pressure PT401-PT408", unit="MPa"),
        SensorMeta(name="x7", description="Differential pressure over VC404, PT408-PT403", unit="MPa"),
        SensorMeta(name="x8", description="FT305 air input flow rate", unit="Sm3/s"),
        SensorMeta(name="x9", description="FT104 water input flow rate", unit="kg/s"),
        SensorMeta(name="x10", description="FT407 flow rate at top of riser", unit="kg/s"),
        SensorMeta(name="x11", description="LI405 level in top separator", unit="m"),
        SensorMeta(name="x12", description="FT406 top separator output flow rate", unit="kg/s"),
        SensorMeta(name="x13", description="FT407 density at top of riser", unit="kg/m3"),
        SensorMeta(name="x14", description="FT406 density at top separator output", unit="kg/m3"),
        SensorMeta(name="x15", description="FT104 density of water input", unit="kg/m3"),
        SensorMeta(name="x16", description="FT407 temperature at top of riser", unit="deg C"),
        SensorMeta(name="x17", description="FT406 temperature at top separator output", unit="deg C"),
        SensorMeta(name="x18", description="FT104 temperature of water input", unit="deg C"),
        SensorMeta(name="x19", description="LI504 gas-liquid level in three-phase separator", unit="%"),
        SensorMeta(name="x20", description="VC501 valve position", unit="%"),
        SensorMeta(name="x21", description="VC302 air valve position", unit="%"),
        SensorMeta(name="x22", description="VC101 water valve position", unit="%"),
        SensorMeta(name="x23", description="PO1 water pump current", unit="A"),
        SensorMeta(name="x24", description="PT417 pressure in mixture zone of 2 inch line", unit="MPa"),
    ]
    return ProcessContext(
        name="CVACaseStudy",
        process_info=(
            "CVACaseStudy is a Cranfield multiphase-flow statistical process "
            "monitoring benchmark with normal training data and six seeded "
            "fault classes under changing operating conditions."
        ),
        sensors=sensors,
        fault_knowledge_path=PROJECT_ROOT / "CVACaseStudy" / "knowledge",
    )

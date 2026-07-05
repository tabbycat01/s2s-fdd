"""Normal-sample reconstruction used by the signal-to-semantics stage."""

from __future__ import annotations

import random

import numpy as np

from .types import ReconstructionResult, TimeSeriesData


def _kmeans_representatives(values: np.ndarray, n_clusters: int, iterations: int = 25) -> np.ndarray:
    """Return representative normal samples using a small numpy-only K-Means."""

    if n_clusters >= len(values):
        return values.copy()

    rng = random.Random(7)
    centers = values[rng.sample(range(len(values)), n_clusters)].copy()
    labels = np.zeros(len(values), dtype=int)

    for _ in range(iterations):
        distances = np.linalg.norm(values[:, None, :] - centers[None, :, :], axis=2)
        labels = np.argmin(distances, axis=1)
        next_centers = centers.copy()
        for cluster in range(n_clusters):
            members = values[labels == cluster]
            if len(members):
                next_centers[cluster] = members.mean(axis=0)
        if np.allclose(next_centers, centers):
            break
        centers = next_centers

    representatives: list[np.ndarray] = []
    for cluster, center in enumerate(centers):
        members = np.where(labels == cluster)[0]
        if len(members) == 0:
            continue
        local = values[members]
        nearest = members[int(np.argmin(np.linalg.norm(local - center, axis=1)))]
        representatives.append(values[nearest])
    return np.vstack(representatives)


class StateMatrixReconstructor:
    """Reconstruct observations as linear combinations of normal states."""

    def __init__(self, n_states: int = 32) -> None:
        self.n_states = n_states
        self.variables: list[str] = []
        self.state_matrix: np.ndarray | None = None

    def fit(self, normal: TimeSeriesData) -> "StateMatrixReconstructor":
        values = np.asarray(normal.values, dtype=float)
        representatives = _kmeans_representatives(values, self.n_states)
        self.state_matrix = representatives.T
        self.variables = list(normal.variables)
        return self

    def reconstruct(self, observed: TimeSeriesData) -> ReconstructionResult:
        if self.state_matrix is None:
            raise RuntimeError("Reconstructor must be fitted before reconstruct().")
        if observed.variables != self.variables:
            raise ValueError("Observed variables do not match fitted variables.")

        matrix = np.asarray(observed.values, dtype=float)
        state = self.state_matrix
        weights = np.linalg.pinv(state) @ matrix.T
        reconstructed = (state @ weights).T
        residuals = matrix - reconstructed
        return ReconstructionResult(
            variables=list(observed.variables),
            timestamps=list(observed.timestamps),
            observed=matrix.tolist(),
            reconstructed=reconstructed.tolist(),
            residuals=residuals.tolist(),
        )

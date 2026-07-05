"""Evaluation helpers for repeated S2S-FDD runs."""

from __future__ import annotations

from collections import Counter


def majority_vote(answers: list[str | None]) -> str | None:
    valid = [answer for answer in answers if answer]
    if not valid:
        return None
    return Counter(valid).most_common(1)[0][0]


def accuracy(predictions: list[str | None], labels: list[str]) -> float:
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length.")
    if not labels:
        return 0.0
    correct = sum(prediction == label for prediction, label in zip(predictions, labels))
    return correct / len(labels)

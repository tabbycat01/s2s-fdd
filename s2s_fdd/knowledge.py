"""Lightweight knowledge retrieval scaffolding for RAG."""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from .types import KnowledgeCase, RetrievedCase, SemanticDescription


TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+")


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def cosine_text_score(query: str, document: str) -> float:
    q = Counter(tokenize(query))
    d = Counter(tokenize(document))
    if not q or not d:
        return 0.0
    numerator = sum(q[token] * d[token] for token in q.keys() & d.keys())
    q_norm = math.sqrt(sum(value * value for value in q.values()))
    d_norm = math.sqrt(sum(value * value for value in d.values()))
    return numerator / max(q_norm * d_norm, 1e-9)


def rewrite_query(description: SemanticDescription) -> str:
    return (
        f"{description.variable} abnormal deviation trend residual exceeds normal "
        f"range. {description.text}"
    )


def chunk_text(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += max(1, size - overlap)
    return chunks


def load_knowledge_cases(path: Path | None) -> list[KnowledgeCase]:
    if path is None or not path.exists():
        return []
    if path.is_dir():
        files = sorted(item for item in path.rglob("*") if item.suffix.lower() in {".txt", ".md", ".html"})
    else:
        files = [path]

    cases: list[KnowledgeCase] = []
    for index, file in enumerate(files, start=1):
        text = file.read_text(encoding="utf-8", errors="ignore")
        cases.append(KnowledgeCase(case_id=f"K{index}", title=file.stem, text=text))
    return cases


class KnowledgeRetriever:
    """Two-stage retrieval placeholder: lexical recall plus parent-case rerank."""

    def __init__(self, cases: list[KnowledgeCase]) -> None:
        self.cases = cases

    def retrieve(self, descriptions: list[SemanticDescription], top_k: int = 3) -> list[RetrievedCase]:
        if not self.cases:
            return []
        query = "\n".join(rewrite_query(description) for description in descriptions)
        candidates: list[RetrievedCase] = []
        for case in self.cases:
            best_score = 0.0
            best_chunk = ""
            for chunk in chunk_text(case.text):
                score = cosine_text_score(query, chunk)
                if score > best_score:
                    best_score = score
                    best_chunk = chunk
            parent_score = 0.7 * best_score + 0.3 * cosine_text_score(query, case.text)
            candidates.append(RetrievedCase(case=case, score=parent_score, matched_chunk=best_chunk))
        return sorted(candidates, key=lambda item: item.score, reverse=True)[:top_k]

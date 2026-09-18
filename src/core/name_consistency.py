"""Name consistency clustering for authors, genres, and titles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from src.utils.text_utils import normalize_author, similarity_ratio


@dataclass
class SimilarGroup:
    """A cluster of similar names with a suggested canonical value."""

    kind: str  # authors | genres | titles
    items: list[tuple[int, str]] = field(default_factory=list)  # id, name
    book_counts: dict[int, int] = field(default_factory=dict)
    suggested_id: int | None = None
    suggested_name: str = ""


def _aggressive_key(name: str) -> str:
    return "".join(ch for ch in (name or "").casefold() if ch.isalnum())


def _cluster_rows(
    rows: list[tuple[int, str, str]],
    *,
    kind: str,
    threshold: float,
    book_counts: dict[int, int],
) -> list[SimilarGroup]:
    if not rows:
        return []

    parent = {item_id: item_id for item_id, _, _ in rows}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Bucket by first character + length band to limit comparisons.
    # Also compare neighboring length bands so near-spellings still meet.
    buckets: dict[tuple[str, int], list[tuple[int, str, str]]] = {}
    for row in rows:
        key = row[2]
        bucket = (key[:1], len(key) // 3)
        buckets.setdefault(bucket, []).append(row)

    def _pair_rows(bucket_rows: list[tuple[int, str, str]]) -> None:
        for i, (id_a, _name_a, key_a) in enumerate(bucket_rows):
            for id_b, _name_b, key_b in bucket_rows[i + 1 :]:
                if abs(len(key_a) - len(key_b)) > 4:
                    continue
                if similarity_ratio(key_a, key_b) >= threshold:
                    union(id_a, id_b)

    for (prefix, band), bucket_rows in list(buckets.items()):
        _pair_rows(bucket_rows)
        neighbor = buckets.get((prefix, band + 1))
        if neighbor:
            _pair_rows(bucket_rows + neighbor)

    clusters: dict[int, list[tuple[int, str]]] = {}
    name_by_id = {item_id: name for item_id, name, _ in rows}
    for item_id, name, _ in rows:
        root = find(item_id)
        clusters.setdefault(root, []).append((item_id, name))

    groups: list[SimilarGroup] = []
    for items in clusters.values():
        if len(items) < 2:
            continue
        suggested_id = max(
            items,
            key=lambda pair: (
                book_counts.get(pair[0], 0),
                len(pair[1]),
            ),
        )[0]
        groups.append(
            SimilarGroup(
                kind=kind,
                items=sorted(items, key=lambda p: p[1].casefold()),
                book_counts={i: book_counts.get(i, 0) for i, _ in items},
                suggested_id=suggested_id,
                suggested_name=name_by_id.get(suggested_id, ""),
            )
        )
    return groups


def find_similar_author_groups(
    authors: Iterable,
    *,
    threshold: float = 0.85,
    book_counts: dict[int, int] | None = None,
) -> list[SimilarGroup]:
    """Cluster authors whose normalized names are similar."""
    book_counts = book_counts or {}
    rows: list[tuple[int, str, str]] = []
    for author in authors:
        author_id = getattr(author, "author_id", None)
        name = (getattr(author, "name", "") or "").strip()
        if author_id is None or not name:
            continue
        key = _aggressive_key(normalize_author(name) or name)
        if not key:
            continue
        rows.append((int(author_id), name, key))
    return _cluster_rows(
        rows, kind="authors", threshold=threshold, book_counts=book_counts
    )


def find_similar_genre_groups(
    genres: Iterable,
    *,
    threshold: float = 0.85,
    book_counts: dict[int, int] | None = None,
) -> list[SimilarGroup]:
    """Cluster genres whose normalized names are similar."""
    book_counts = book_counts or {}
    rows: list[tuple[int, str, str]] = []
    for genre in genres:
        genre_id = getattr(genre, "genre_id", None)
        name = (getattr(genre, "name", "") or "").strip()
        if genre_id is None or not name:
            continue
        key = _aggressive_key(name)
        if not key:
            continue
        rows.append((int(genre_id), name, key))
    return _cluster_rows(
        rows, kind="genres", threshold=threshold, book_counts=book_counts
    )

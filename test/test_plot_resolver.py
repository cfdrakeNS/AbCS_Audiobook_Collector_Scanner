"""Focused tests for Batch A plot candidates and diagnostics."""

from __future__ import annotations

from src.web.plot_resolver import (
    PlotCandidate,
    PlotFetchDiagnostics,
    PlotResolver,
    candidate_identifiers,
    candidate_provenance,
)


def test_candidate_records_provenance_without_plot_text():
    candidate = PlotCandidate(
        text="A" * 90,
        source="open_library",
        identifiers={"open_library_work_key": "/works/OL1W"},
        source_url="https://openlibrary.org/works/OL1W",
        fetched_at="2026-09-29T12:00:00+00:00",
        license_id="terms-review-required",
    )
    candidate.normalized_text = candidate.text

    record = candidate.diagnostic_record()

    assert record["source_url"] == "https://openlibrary.org/works/OL1W"
    assert record["fetched_at"] == "2026-09-29T12:00:00+00:00"
    assert record["license_id"] == "terms-review-required"
    assert "text" not in record


def test_resolver_records_normalization_and_rejection_reason():
    resolver = PlotResolver(min_length=20)
    candidate = PlotCandidate(
        text="<p>No description available</p>",
        source="open_library",
    )

    resolver.evaluate(candidate, db_author="", author_matches=lambda *_: True)

    assert candidate.normalized_text == "No description available"
    assert candidate.modified
    assert candidate.rejection_reason == "stub"


def test_diagnostics_record_selected_source():
    diagnostics = PlotFetchDiagnostics("Title", "Author")
    rejected = PlotCandidate("Short", "open_library", rejection_reason="too_short")
    accepted = PlotCandidate("A" * 90, "wikipedia")

    diagnostics.record(rejected)
    diagnostics.record(accepted)
    diagnostics.select(accepted)

    snapshot = diagnostics.snapshot()

    assert snapshot["selected_source"] == "wikipedia"
    assert snapshot["candidates"][0]["rejection_reason"] == "too_short"
    assert snapshot["candidates"][1]["accepted"]


def test_resolver_ranks_identity_before_source_and_plot_length():
    resolver = PlotResolver(min_length=20)
    weak_long = PlotCandidate(
        "L" * 400,
        "open_library",
        match_confidence="title",
        normalized_text="L" * 400,
    )
    exact_short = PlotCandidate(
        "I" * 90,
        "wikipedia",
        match_confidence="identifier",
        normalized_text="I" * 90,
    )

    assert resolver.choose([weak_long, exact_short]) is exact_short


def test_resolver_uses_stable_source_tiebreak_for_equal_candidates():
    resolver = PlotResolver(min_length=20)
    first = PlotCandidate(
        "A" * 100,
        "google_books",
        match_confidence="title_author",
        normalized_text="A" * 100,
    )
    second = PlotCandidate(
        "B" * 100,
        "google_books",
        match_confidence="title_author",
        normalized_text="B" * 100,
    )

    assert resolver.choose([first, second]) is first


def test_identifier_and_provenance_helpers_ignore_empty_values():
    metadata = {
        "isbn": "9780000000000",
        "identifiers": {"wikidata_id": "Q1", "empty": ""},
        "plot_source_url": "https://example.test/book",
        "plot_license_id": "terms-review-required",
    }

    assert candidate_identifiers(metadata) == {
        "wikidata_id": "Q1",
        "isbn": "9780000000000",
    }
    assert candidate_provenance(metadata) == {
        "plot_source_url": "https://example.test/book",
        "plot_license_id": "terms-review-required",
    }
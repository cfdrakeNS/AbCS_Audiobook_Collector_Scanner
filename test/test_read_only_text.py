"""Tests for navigable plot/text formatting."""

from src.accessibility.read_only_text import (
    format_plot_text_for_navigation,
    plot_lines_for_review,
    plot_text_equivalent,
    restore_prose_line_breaks,
)


def test_format_plot_preserves_prose():
    text = "First sentence. Second sentence! Third one?"
    formatted = format_plot_text_for_navigation(text)
    assert formatted == text


def test_format_plot_keeps_long_sentence_on_one_line():
    text = (
        "Through twenty-one novels featuring Lucas Davenport, Kidd, or the "
        "razor-edge world of the Night Crew, John Sandford has been writing."
    )
    formatted = format_plot_text_for_navigation(text)
    assert formatted == text


def test_restore_prose_rejoins_sentence_per_line_text():
    text = (
        "Rating: 3.5 (2 ratings)\n"
        "Sometimes, justice isn't enough.\n"
        "Through twenty-one novels featuring Lucas Davenport.\n"
        "But Dead Watch sets a whole new level."
    )
    restored = restore_prose_line_breaks(text)
    assert restored.startswith("Rating: 3.5 (2 ratings)\n")
    assert "Sometimes, justice isn't enough. Through twenty-one" in restored
    assert "\nBut Dead Watch" not in restored or restored.count("\n") == 1


def test_format_plot_preserves_existing_lines():
    text = "Line one.\nLine two."
    assert format_plot_text_for_navigation(text) == "Line one.\nLine two."


def test_format_plot_splits_rating_prefix():
    text = "Rating: 4.5 (1,234 ratings) - First sentence. Second sentence."
    formatted = format_plot_text_for_navigation(text)
    assert formatted.startswith("Rating: 4.5 (1,234 ratings)\n")
    assert "First sentence. Second sentence." in formatted


def test_format_plot_keeps_unbroken_text_on_one_line():
    text = " ".join(["word"] * 30)
    formatted = format_plot_text_for_navigation(text)
    assert formatted == text


def test_plot_line_list_puts_rating_first_then_wrapped_body():
    from PySide6.QtWidgets import QApplication

    from src.accessibility.read_only_text import PlotLineList

    app = QApplication.instance() or QApplication([])
    widget = PlotLineList()
    widget.set_plot_text("Rating: 4.0\nFirst sentence. Second sentence.")
    assert widget.count() >= 2
    assert widget.item(0).text() == "Rating: 4.0"
    assert all(len(widget.item(i).text()) <= 73 for i in range(1, widget.count()))
    body = " ".join(widget.item(i).text() for i in range(1, widget.count()))
    assert "First sentence. Second sentence." == body


def test_plot_lines_for_review_wraps_at_seventy_three_chars():
    text = " ".join(["word"] * 30)
    lines = plot_lines_for_review(text)
    assert lines
    assert all(len(line) <= 73 for line in lines)
    assert " ".join(lines) == text


def test_plot_lines_for_review_does_not_break_words():
    long_word = "supercalifragilisticexpialidocious"
    assert plot_lines_for_review(long_word) == [long_word]
    text = (
        "Through twenty-one novels featuring Lucas Davenport, Kidd, or the "
        "razor-edge world of the Night Crew, John Sandford has been writing."
    )
    lines = plot_lines_for_review(text)
    assert " ".join(lines) == text
    assert all(len(line) <= 73 for line in lines)


def test_plot_text_equivalent_ignores_line_breaks():
    left = "Rating: 4.0 - One sentence. Two sentence."
    right = "Rating: 4.0 - One sentence.\nTwo sentence."
    assert plot_text_equivalent(left, right)

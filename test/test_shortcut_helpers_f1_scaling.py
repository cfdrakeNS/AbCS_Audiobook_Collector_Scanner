"""F1 shortcut popup scaling helpers."""

from src.accessibility.shortcut_helpers import scaled_f1_popup_font_point_size


def test_scaled_f1_popup_font_point_size():
    assert scaled_f1_popup_font_point_size(12, 100) == 12
    assert scaled_f1_popup_font_point_size(12, 150) == 18
    assert scaled_f1_popup_font_point_size(11, 200) == 22

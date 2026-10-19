import os

import airfoil_splines_settings as config


SELECTED_FILENAME_MAX_LENGTH = 24


def selected_filename_label(file_path: str) -> str:
    """Return a compact filename stem suitable for the Fusion button."""
    stem = os.path.splitext(os.path.basename(file_path))[0]
    if len(stem) <= SELECTED_FILENAME_MAX_LENGTH:
        return stem
    return stem[:SELECTED_FILENAME_MAX_LENGTH - 1] + '…'


def set_float_input_value(input_control, value: float) -> None:
    """Set a unitless float input using a stable display expression."""
    input_control.expression = format(float(value), '.10g')


def smoothing_from_input(input_control) -> float:
    """Translate the human-friendly smoothing slider to its fitter weight."""
    return int(input_control.valueOne) / config.SMOOTHNESS_UI_SCALE


def set_smoothing_input_value(input_control, smoothing: float) -> None:
    """Show a fitter smoothing weight as an integer from 0 through 100."""
    ui_value = round(float(smoothing) * config.SMOOTHNESS_UI_SCALE)
    input_control.valueOne = max(config.MIN_SMOOTHNESS_UI,
                                 min(config.MAX_SMOOTHNESS_UI, ui_value))

import os


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

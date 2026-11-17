"""Plots of the audio analysis, drawn on matplotlib Axes."""

import numpy as np
from matplotlib.axes import Axes


def plot_spectrum(axes: Axes, frequencies: np.ndarray, magnitudes: np.ndarray) -> None:
    """Draw the amplitude spectrum as a line on the given axes.

    The axes start at 0 Hz and at an amplitude of 0 and end at the highest
    frequency, so that no impossible values are shown. Colors are left to the
    style of the caller.
    """
    axes.plot(frequencies, magnitudes)
    axes.set_xlim(0, frequencies[-1])
    axes.set_ylim(bottom=0)
    axes.set_xlabel("Frequency (Hz)")
    axes.set_ylabel("Amplitude")
    axes.set_title("Frequency spectrum")

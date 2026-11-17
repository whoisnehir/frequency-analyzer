"""Tests for the plots, drawn without opening a window."""

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from frequency_analyzer.analysis import compute_spectrum
from frequency_analyzer.plots import plot_spectrum

SAMPLE_RATE = 8000


def _draw_spectrum_of_tone(frequency):
    """Draw the spectrum of a one-second tone on an off-screen figure."""
    time = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    samples = 0.5 * np.sin(2 * np.pi * frequency * time)
    frequencies, magnitudes = compute_spectrum(samples, SAMPLE_RATE)

    figure = Figure()
    FigureCanvasAgg(figure)
    axes = figure.add_subplot()
    plot_spectrum(axes, frequencies, magnitudes)
    figure.canvas.draw()
    return axes, frequencies, magnitudes


def test_spectrum_is_drawn_as_one_line_with_the_given_data():
    axes, frequencies, magnitudes = _draw_spectrum_of_tone(440)

    assert len(axes.lines) == 1
    line = axes.lines[0]
    np.testing.assert_array_equal(line.get_xdata(), frequencies)
    np.testing.assert_array_equal(line.get_ydata(), magnitudes)


def test_axes_have_labels_and_a_title():
    axes, _, _ = _draw_spectrum_of_tone(440)

    assert axes.get_xlabel() == "Frequency (Hz)"
    assert axes.get_ylabel() == "Amplitude"
    assert axes.get_title() == "Frequency spectrum"


def test_axes_go_from_zero_to_the_highest_frequency():
    axes, _, magnitudes = _draw_spectrum_of_tone(440)

    assert axes.get_xlim() == (0, SAMPLE_RATE / 2)
    bottom, top = axes.get_ylim()
    assert bottom == 0
    assert top >= magnitudes.max()

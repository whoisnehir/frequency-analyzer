"""Tests for the plots inside the tkinter window."""

import tkinter as tk

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from scipy.io import wavfile

from frequency_analyzer.gui import AnalyzerWindow, draw_analysis

SAMPLE_RATE = 8000


def _tone(frequency):
    """Return a one-second tone of amplitude 0.5."""
    time = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    return 0.5 * np.sin(2 * np.pi * frequency * time)


def _draw_on_new_figure(samples):
    """Draw the analysis of the samples on an off-screen figure."""
    figure = Figure(layout="constrained")
    FigureCanvasAgg(figure)
    draw_analysis(figure, samples, SAMPLE_RATE)
    figure.canvas.draw()
    return figure


def test_analysis_has_three_plots_and_a_color_bar():
    figure = _draw_on_new_figure(_tone(440))

    titles = [axes.get_title() for axes in figure.axes]
    assert titles == ["Waveform", "Frequency spectrum", "Spectrogram", ""]
    assert figure.axes[3].get_ylabel() == "Amplitude"


def test_spectrogram_is_below_the_other_plots_across_the_whole_width():
    figure = _draw_on_new_figure(_tone(440))
    waveform, spectrum, spectrogram = [axes.get_position() for axes in figure.axes[:3]]

    assert waveform.x1 < spectrum.x0
    assert spectrogram.y1 < min(waveform.y0, spectrum.y0)
    assert spectrogram.x0 == pytest.approx(waveform.x0, abs=0.02)
    assert spectrogram.x1 > spectrum.x0


def test_drawing_again_replaces_the_previous_plots():
    figure = _draw_on_new_figure(_tone(440))

    draw_analysis(figure, _tone(880), SAMPLE_RATE)

    assert len(figure.axes) == 4
    waveform_line = figure.axes[0].lines[0]
    np.testing.assert_array_equal(waveform_line.get_ydata(), _tone(880))


@pytest.fixture
def root():
    """Create a hidden tkinter window and close it after the test."""
    window = tk.Tk()
    window.withdraw()
    yield window
    window.destroy()


def test_window_shows_the_plots_and_the_name_of_a_file(root, tmp_path):
    path = tmp_path / "tone.wav"
    wavfile.write(path, SAMPLE_RATE, np.round(_tone(440) * 32767).astype(np.int16))
    window = AnalyzerWindow(root)

    window.show_file(path)

    assert root.title() == "tone.wav"
    titles = [axes.get_title() for axes in window.figure.axes]
    assert titles == ["Waveform", "Frequency spectrum", "Spectrogram", ""]
    assert window.canvas.get_tk_widget().master is root
    assert not window.figure.stale

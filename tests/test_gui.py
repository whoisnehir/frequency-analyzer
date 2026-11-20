"""Tests for the plots inside the tkinter window."""

import tkinter as tk
from tkinter import filedialog

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


@pytest.fixture(scope="module")
def tk_root():
    """Create one hidden tkinter root window for all the tests of this file."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def root(tk_root):
    """Create a hidden window for one test and close it after the test."""
    window = tk.Toplevel(tk_root)
    window.withdraw()
    yield window
    window.destroy()


def _write_tone(path, frequency=440):
    """Write a one-second tone as a 16-bit WAV file."""
    samples = np.round(_tone(frequency) * 32767).astype(np.int16)
    wavfile.write(path, SAMPLE_RATE, samples)
    return path


def test_window_shows_the_app_name_and_a_hint_before_a_file_is_opened(root):
    window = AnalyzerWindow(root)

    assert root.title() == "Frequency Analyzer"
    hints = [text.get_text() for text in window.figure.texts]
    assert window.file_label.cget("text") == "No file loaded"
    assert window.frequency_label.cget("text") == ""
    assert hints == ["Open a WAV file to see its waveform, spectrum and spectrogram"]


def test_window_shows_the_plots_and_the_name_of_a_file(root, tmp_path):
    path = _write_tone(tmp_path / "tone.wav")
    window = AnalyzerWindow(root)

    window.show_file(path)

    assert root.title() == "tone.wav - Frequency Analyzer"
    titles = [axes.get_title() for axes in window.figure.axes]
    assert window.file_label.cget("text") == "tone.wav"
    assert titles == ["Waveform", "Frequency spectrum", "Spectrogram", ""]
    assert window.figure.texts == []
    assert window.canvas.get_tk_widget().master is root
    assert not window.figure.stale


def test_open_button_shows_the_wav_file_chosen_in_the_dialog(
    root, tmp_path, monkeypatch
):
    path = _write_tone(tmp_path / "chosen.wav")
    dialog_options = {}

    def choose(**options):
        dialog_options.update(options)
        return str(path)

    monkeypatch.setattr(filedialog, "askopenfilename", choose)
    window = AnalyzerWindow(root)

    window.open_button.invoke()

    assert dialog_options["filetypes"] == [("WAV files", "*.wav")]
    assert window.file_label.cget("text") == "chosen.wav"
    assert root.title() == "chosen.wav - Frequency Analyzer"


def test_cancelled_dialog_keeps_the_current_file(root, tmp_path, monkeypatch):
    window = AnalyzerWindow(root)
    window.show_file(_write_tone(tmp_path / "tone.wav"))
    waveform = window.figure.axes[0].lines[0].get_ydata()
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **options: "")

    window.choose_file()

    assert window.file_label.cget("text") == "tone.wav"
    assert root.title() == "tone.wav - Frequency Analyzer"
    assert window.figure.axes[0].lines[0].get_ydata() is waveform


def test_toolbar_is_below_the_plots_without_the_subplots_button(root):
    window = AnalyzerWindow(root)

    buttons = [item[0] for item in window.toolbar.toolitems if item[0] is not None]
    assert buttons == ["Home", "Back", "Forward", "Pan", "Zoom", "Save"]
    assert window.toolbar.master is root
    assert window.toolbar.pack_info()["side"] == "bottom"


def _zoom_into_the_spectrum(window):
    """Zoom into 400-480 Hz as the Zoom button does, which saves both views."""
    window.toolbar.push_current()
    window.figure.axes[1].set_xlim(400, 480)
    window.toolbar.push_current()


def test_home_shows_the_whole_new_file_after_zooming_into_the_previous_one(
    root, tmp_path
):
    window = AnalyzerWindow(root)
    window.show_file(_write_tone(tmp_path / "first.wav"))
    _zoom_into_the_spectrum(window)
    window.show_file(_write_tone(tmp_path / "second.wav"))
    _zoom_into_the_spectrum(window)

    window.toolbar.home()

    assert window.figure.axes[1].get_xlim() == (0, SAMPLE_RATE / 2)


def test_window_shows_the_dominant_frequency_of_each_file(root, tmp_path):
    window = AnalyzerWindow(root)

    window.show_file(_write_tone(tmp_path / "a4.wav", 440))
    first = window.frequency_label.cget("text")
    window.show_file(_write_tone(tmp_path / "a5.wav", 880))

    assert first == "Dominant frequency: 440.0 Hz"
    assert window.frequency_label.cget("text") == "Dominant frequency: 880.0 Hz"
    assert window.frequency_label.pack_info()["side"] == "right"


def test_analysis_in_decibels_draws_the_spectrum_and_the_spectrogram_in_db():
    figure = Figure(layout="constrained")
    FigureCanvasAgg(figure)

    draw_analysis(figure, _tone(440), SAMPLE_RATE, decibels=True)

    waveform, spectrum, spectrogram, color_bar = figure.axes
    assert waveform.get_ylabel() == "Amplitude"
    assert spectrum.get_ylabel() == "Amplitude (dB)"
    assert spectrum.lines[0].get_ydata().max() == pytest.approx(-6.02, abs=0.1)
    assert color_bar.get_ylabel() == "Amplitude (dB)"
    mesh = spectrogram.collections[0]
    assert mesh.get_array().max() == pytest.approx(-6.02, abs=0.1)
    assert mesh.get_clim() == (-120, 0)


def test_decibels_box_switches_the_plots_of_the_current_file(root, tmp_path):
    window = AnalyzerWindow(root)
    window.show_file(_write_tone(tmp_path / "tone.wav"))

    window.decibels_button.invoke()
    in_decibels = window.figure.axes[1].get_ylabel()
    window.decibels_button.invoke()

    assert in_decibels == "Amplitude (dB)"
    assert window.figure.axes[1].get_ylabel() == "Amplitude"
    assert not window.figure.stale


def test_decibels_box_does_nothing_before_a_file_is_opened(root):
    window = AnalyzerWindow(root)

    window.decibels.set(True)
    window.redraw()

    assert window.figure.axes == []
    hints = [text.get_text() for text in window.figure.texts]
    assert hints == ["Open a WAV file to see its waveform, spectrum and spectrogram"]

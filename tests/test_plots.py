"""Tests for the plots, drawn without opening a window."""

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from frequency_analyzer.analysis import (
    compute_spectrogram,
    compute_spectrum,
    to_decibels,
)
from frequency_analyzer.plots import plot_spectrogram, plot_spectrum, plot_waveform

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


def _draw_waveform_of_tone(frequency):
    """Draw the waveform of a one-second tone on an off-screen figure."""
    time = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    samples = 0.5 * np.sin(2 * np.pi * frequency * time)

    figure = Figure()
    FigureCanvasAgg(figure)
    axes = figure.add_subplot()
    plot_waveform(axes, samples, SAMPLE_RATE)
    figure.canvas.draw()
    return axes, samples


def test_waveform_is_drawn_as_one_line_against_time():
    axes, samples = _draw_waveform_of_tone(440)

    assert len(axes.lines) == 1
    line = axes.lines[0]
    np.testing.assert_allclose(line.get_xdata(), np.arange(SAMPLE_RATE) / SAMPLE_RATE)
    np.testing.assert_array_equal(line.get_ydata(), samples)


def test_waveform_axes_have_labels_and_a_title():
    axes, _ = _draw_waveform_of_tone(440)

    assert axes.get_xlabel() == "Time (s)"
    assert axes.get_ylabel() == "Amplitude"
    assert axes.get_title() == "Waveform"


def test_waveform_axes_go_from_zero_to_the_last_sample_and_full_scale():
    axes, _ = _draw_waveform_of_tone(440)

    assert axes.get_xlim() == (0, (SAMPLE_RATE - 1) / SAMPLE_RATE)
    assert axes.get_ylim() == (-1, 1)


def _draw_spectrogram_of_tones(sample_rate):
    """Draw the spectrogram of a 440 Hz tone followed by an 880 Hz tone."""
    time = np.arange(sample_rate // 2) / sample_rate
    samples = np.concatenate(
        [0.5 * np.sin(2 * np.pi * 440 * time), 0.5 * np.sin(2 * np.pi * 880 * time)]
    )
    times, frequencies, magnitudes = compute_spectrogram(samples, sample_rate)

    figure = Figure()
    FigureCanvasAgg(figure)
    axes = figure.add_subplot()
    plot_spectrogram(axes, times, frequencies, magnitudes)
    figure.canvas.draw()
    return axes, magnitudes


def test_spectrogram_is_drawn_as_an_image_of_the_magnitudes():
    axes, magnitudes = _draw_spectrogram_of_tones(SAMPLE_RATE)

    assert len(axes.collections) == 1
    mesh = axes.collections[0]
    np.testing.assert_array_equal(mesh.get_array(), magnitudes)
    assert mesh.get_cmap().name == "magma"


def test_spectrogram_has_labels_a_title_and_a_color_bar():
    axes, _ = _draw_spectrogram_of_tones(SAMPLE_RATE)

    assert axes.get_xlabel() == "Time (s)"
    assert axes.get_ylabel() == "Frequency (Hz)"
    assert axes.get_title() == "Spectrogram"
    color_bar_axes = axes.figure.axes[1]
    assert color_bar_axes.get_ylabel() == "Amplitude"


def test_spectrogram_frequency_axis_stops_at_5000_hz():
    axes, _ = _draw_spectrogram_of_tones(44100)

    assert axes.get_ylim() == (0, 5000)


def test_spectrogram_frequency_axis_stops_at_nyquist_below_5000_hz():
    axes, _ = _draw_spectrogram_of_tones(SAMPLE_RATE)

    assert axes.get_ylim() == (0, SAMPLE_RATE / 2)


def _new_axes():
    """Return the axes of a new off-screen figure."""
    figure = Figure()
    FigureCanvasAgg(figure)
    return figure.add_subplot()


def test_spectrum_in_decibels_goes_from_the_floor_to_0_db():
    time = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    frequencies, magnitudes = compute_spectrum(
        0.5 * np.sin(2 * np.pi * 440 * time), SAMPLE_RATE
    )
    axes = _new_axes()

    plot_spectrum(axes, frequencies, to_decibels(magnitudes), decibels=True)

    np.testing.assert_array_equal(axes.lines[0].get_ydata(), to_decibels(magnitudes))
    assert axes.get_ylim() == (-120, 0)
    assert axes.get_ylabel() == "Amplitude (dB)"


def test_spectrogram_in_decibels_colors_from_the_floor_to_0_db():
    time = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    times, frequencies, magnitudes = compute_spectrogram(
        0.5 * np.sin(2 * np.pi * 440 * time), SAMPLE_RATE
    )
    axes = _new_axes()

    plot_spectrogram(axes, times, frequencies, to_decibels(magnitudes), decibels=True)

    assert axes.collections[0].get_clim() == (-120, 0)
    assert axes.figure.axes[1].get_ylabel() == "Amplitude (dB)"

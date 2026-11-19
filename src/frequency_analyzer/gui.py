"""Desktop window that shows the plots of a WAV file."""

import numpy as np
from matplotlib.figure import Figure

from frequency_analyzer.analysis import compute_spectrogram, compute_spectrum
from frequency_analyzer.plots import plot_spectrogram, plot_spectrum, plot_waveform


def draw_analysis(figure: Figure, samples: np.ndarray, sample_rate: int) -> None:
    """Draw the waveform, the spectrum and the spectrogram on the given figure.

    The waveform and the spectrum are side by side, and the spectrogram is below
    them across the whole width. Anything already on the figure is removed
    first, so that the same figure can show one file after another.
    """
    figure.clear()
    grid = figure.add_gridspec(2, 2)
    waveform_axes = figure.add_subplot(grid[0, 0])
    spectrum_axes = figure.add_subplot(grid[0, 1])
    spectrogram_axes = figure.add_subplot(grid[1, :])

    plot_waveform(waveform_axes, samples, sample_rate)
    plot_spectrum(spectrum_axes, *compute_spectrum(samples, sample_rate))
    plot_spectrogram(spectrogram_axes, *compute_spectrogram(samples, sample_rate))

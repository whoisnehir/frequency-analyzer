"""Plots of the audio analysis, drawn on matplotlib Axes."""

import numpy as np
from matplotlib.axes import Axes

from frequency_analyzer.analysis import DECIBEL_FLOOR

SPECTROGRAM_MAX_FREQUENCY = 5000


def plot_spectrum(
    axes: Axes,
    frequencies: np.ndarray,
    magnitudes: np.ndarray,
    decibels: bool = False,
) -> None:
    """Draw the amplitude spectrum as a line on the given axes.

    The axes start at 0 Hz and at an amplitude of 0 and end at the highest
    frequency, so that no impossible values are shown. With decibels=True, the
    magnitudes are in dB and the amplitude axis goes from DECIBEL_FLOOR to 0 dB.
    Colors are left to the style of the caller.
    """
    axes.plot(frequencies, magnitudes)
    axes.set_xlim(0, frequencies[-1])
    if decibels:
        axes.set_ylim(DECIBEL_FLOOR, 0)
        axes.set_ylabel("Amplitude (dB)")
    else:
        axes.set_ylim(bottom=0)
        axes.set_ylabel("Amplitude")
    axes.set_xlabel("Frequency (Hz)")
    axes.set_title("Frequency spectrum")


def plot_waveform(axes: Axes, samples: np.ndarray, sample_rate: int) -> None:
    """Draw the samples against time as a line on the given axes.

    The time axis goes from 0 to the last sample, and the amplitude axis is fixed
    from -1 to 1 (full scale), so that the plot shows how loud the sound is.
    Colors are left to the style of the caller.
    """
    times = np.arange(len(samples)) / sample_rate
    axes.plot(times, samples)
    axes.set_xlim(0, times[-1])
    axes.set_ylim(-1, 1)
    axes.set_xlabel("Time (s)")
    axes.set_ylabel("Amplitude")
    axes.set_title("Waveform")


def plot_spectrogram(
    axes: Axes,
    times: np.ndarray,
    frequencies: np.ndarray,
    magnitudes: np.ndarray,
    decibels: bool = False,
) -> None:
    """Draw the spectrogram as an image on the given axes, with a color bar.

    Each segment is a column and each frequency a row, colored by its amplitude
    with the magma colormap. The frequency axis stops at 5000 Hz, or at the
    highest frequency if it is lower, where most of the content of music and
    speech lies. With decibels=True, the magnitudes are in dB and the colors go
    from DECIBEL_FLOOR to 0 dB.
    """
    mesh = axes.pcolormesh(
        times, frequencies, magnitudes, shading="nearest", cmap="magma"
    )
    if decibels:
        mesh.set_clim(DECIBEL_FLOOR, 0)
    label = "Amplitude (dB)" if decibels else "Amplitude"
    axes.figure.colorbar(mesh, ax=axes, label=label)
    axes.set_ylim(0, min(SPECTROGRAM_MAX_FREQUENCY, frequencies[-1]))
    axes.set_xlabel("Time (s)")
    axes.set_ylabel("Frequency (Hz)")
    axes.set_title("Spectrogram")

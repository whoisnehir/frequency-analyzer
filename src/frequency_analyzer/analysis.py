"""Frequency spectrum of audio samples and its strongest frequency."""

import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import get_window


def compute_spectrum(
    samples: np.ndarray, sample_rate: int
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the amplitude spectrum of a signal.

    The mean of the samples is removed first, so that a constant offset does
    not appear at 0 Hz. A Hann window reduces the leakage between frequencies,
    and the magnitudes are scaled so that a sine wave of amplitude A peaks at
    about A.

    Returns the frequencies in Hz and the magnitude at each of them.
    """
    centered = samples - samples.mean()
    window = get_window("hann", len(samples))
    spectrum = rfft(centered * window)
    frequencies = rfftfreq(len(samples), d=1 / sample_rate)
    magnitudes = 2 * np.abs(spectrum) / window.sum()
    return frequencies, magnitudes


def dominant_frequency(frequencies: np.ndarray, magnitudes: np.ndarray) -> float:
    """Return the frequency with the largest magnitude."""
    return float(frequencies[np.argmax(magnitudes)])

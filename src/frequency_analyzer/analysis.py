"""Frequency spectrum of audio samples and its strongest frequency."""

import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import get_window

SEGMENT_DURATION = 0.05


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


def compute_spectrogram(
    samples: np.ndarray, sample_rate: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute the amplitude spectrum of short, overlapping segments of a signal.

    The samples are split into 50 ms segments, a new one starting every 25 ms,
    and each segment goes through compute_spectrum, so that the window and the
    scaling are the same as for the spectrum of the whole signal.

    Returns the time of the middle of each segment in seconds, the frequencies
    in Hz and the magnitudes, with one row per frequency and one column per
    segment.
    """
    segment_length = round(SEGMENT_DURATION * sample_rate)
    if len(samples) < segment_length:
        raise ValueError("The signal is shorter than one segment.")
    hop = segment_length // 2
    starts = range(0, len(samples) - segment_length + 1, hop)

    columns = []
    for start in starts:
        segment = samples[start : start + segment_length]
        _, magnitudes = compute_spectrum(segment, sample_rate)
        columns.append(magnitudes)

    times = (np.array(starts) + segment_length / 2) / sample_rate
    frequencies = rfftfreq(segment_length, d=1 / sample_rate)
    return times, frequencies, np.column_stack(columns)

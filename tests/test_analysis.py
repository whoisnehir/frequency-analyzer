"""Tests for the frequency spectrum."""

import numpy as np
import pytest

from frequency_analyzer.analysis import compute_spectrum, dominant_frequency

SAMPLE_RATE = 8000


def _sine(frequency, amplitude=1.0, duration=1.0):
    """Generate a sine wave sampled at SAMPLE_RATE."""
    time = np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE
    return amplitude * np.sin(2 * np.pi * frequency * time)


def test_spectrum_goes_from_0_hz_to_half_the_sample_rate():
    frequencies, magnitudes = compute_spectrum(_sine(440), SAMPLE_RATE)

    assert frequencies.shape == magnitudes.shape
    assert frequencies[0] == 0
    assert frequencies[-1] == SAMPLE_RATE / 2


def test_single_tone_peaks_at_its_frequency():
    frequencies, magnitudes = compute_spectrum(_sine(440), SAMPLE_RATE)

    assert dominant_frequency(frequencies, magnitudes) == 440


def test_mix_of_tones_has_a_peak_at_each_frequency():
    samples = _sine(300, 0.5) + _sine(1000, 0.3) + _sine(2500, 0.2)

    frequencies, magnitudes = compute_spectrum(samples, SAMPLE_RATE)

    for frequency, amplitude in [(300, 0.5), (1000, 0.3), (2500, 0.2)]:
        peak = magnitudes[frequencies == frequency][0]
        assert peak == pytest.approx(amplitude, rel=0.01)
    assert dominant_frequency(frequencies, magnitudes) == 300


@pytest.mark.parametrize("duration", [0.5, 1.0, 2.0])
def test_peak_equals_the_amplitude_whatever_the_duration(duration):
    samples = _sine(440, amplitude=0.5, duration=duration)

    _, magnitudes = compute_spectrum(samples, SAMPLE_RATE)

    assert magnitudes.max() == pytest.approx(0.5, rel=0.01)


def test_constant_offset_does_not_change_the_dominant_frequency():
    samples = 0.1 + _sine(440, amplitude=0.05)

    frequencies, magnitudes = compute_spectrum(samples, SAMPLE_RATE)

    assert dominant_frequency(frequencies, magnitudes) == 440
    assert magnitudes[0] == pytest.approx(0, abs=1e-9)


def test_tone_between_two_frequencies_does_not_leak_far_away():
    frequencies, magnitudes = compute_spectrum(_sine(440.5), SAMPLE_RATE)

    far_away = magnitudes[frequencies == 600][0]

    assert far_away < 1e-4

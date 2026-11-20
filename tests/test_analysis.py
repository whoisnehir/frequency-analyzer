"""Tests for the frequency spectrum."""

import numpy as np
import pytest

from frequency_analyzer.analysis import (
    compute_spectrogram,
    compute_spectrum,
    dominant_frequency,
    to_decibels,
)

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


def test_spectrogram_uses_50_ms_segments_every_25_ms():
    times, frequencies, magnitudes = compute_spectrogram(_sine(440), SAMPLE_RATE)

    assert times[0] == pytest.approx(0.025)
    np.testing.assert_allclose(np.diff(times), 0.025)
    assert frequencies[1] == pytest.approx(20)
    assert magnitudes.shape == (len(frequencies), len(times))


def test_spectrogram_follows_tones_over_time():
    samples = np.concatenate([_sine(440, duration=0.5), _sine(880, duration=0.5)])

    times, frequencies, magnitudes = compute_spectrogram(samples, SAMPLE_RATE)

    strongest = frequencies[magnitudes.argmax(axis=0)]
    assert np.all(strongest[times < 0.45] == 440)
    assert np.all(strongest[times > 0.55] == 880)


def test_spectrogram_peak_equals_the_amplitude():
    _, _, magnitudes = compute_spectrogram(_sine(440, amplitude=0.5), SAMPLE_RATE)

    np.testing.assert_allclose(magnitudes.max(axis=0), 0.5, rtol=0.01)


def test_signal_shorter_than_one_segment_is_rejected():
    with pytest.raises(ValueError, match="shorter than one segment"):
        compute_spectrogram(_sine(440, duration=0.01), SAMPLE_RATE)


def test_amplitudes_are_converted_to_decibels():
    decibels = to_decibels(np.array([1.0, 0.5, 0.1, 0.001]))

    np.testing.assert_allclose(decibels, [0.0, -6.0206, -20.0, -60.0], atol=1e-4)


def test_silence_stays_at_the_decibel_floor():
    decibels = to_decibels(np.array([0.0, 1e-9]))

    np.testing.assert_array_equal(decibels, [-120.0, -120.0])


def test_spectrogram_table_keeps_its_shape_in_decibels():
    _, _, magnitudes = compute_spectrogram(_sine(440, amplitude=0.5), SAMPLE_RATE)

    decibels = to_decibels(magnitudes)

    assert decibels.shape == magnitudes.shape
    assert decibels.max() == pytest.approx(-6.02, abs=0.1)

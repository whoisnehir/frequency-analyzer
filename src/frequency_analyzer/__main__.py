"""Command-line entry point: python -m frequency_analyzer <file.wav>."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from frequency_analyzer.analysis import (
    compute_spectrogram,
    compute_spectrum,
    dominant_frequency,
)
from frequency_analyzer.audio import load_wav
from frequency_analyzer.plots import plot_spectrogram, plot_spectrum, plot_waveform


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Read the path of the WAV file from the command line."""
    parser = argparse.ArgumentParser(
        prog="python -m frequency_analyzer",
        description="Show the frequency spectrum of a WAV file.",
    )
    parser.add_argument("path", type=Path, help="path of the WAV file to analyze")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Analyze a WAV file, print its dominant frequency and show its plots."""
    args = parse_args(argv)
    samples, sample_rate = load_wav(args.path)
    frequencies, magnitudes = compute_spectrum(samples, sample_rate)
    dominant = dominant_frequency(frequencies, magnitudes)
    print(f"Dominant frequency: {dominant:.1f} Hz")

    figure = plt.figure(figsize=(11, 7.5), layout="constrained")
    figure.canvas.manager.set_window_title(args.path.name)
    grid = figure.add_gridspec(2, 2)
    waveform_axes = figure.add_subplot(grid[0, 0])
    spectrum_axes = figure.add_subplot(grid[0, 1])
    spectrogram_axes = figure.add_subplot(grid[1, :])

    plot_waveform(waveform_axes, samples, sample_rate)
    plot_spectrum(spectrum_axes, frequencies, magnitudes)
    plot_spectrogram(spectrogram_axes, *compute_spectrogram(samples, sample_rate))
    plt.show()


if __name__ == "__main__":
    main()

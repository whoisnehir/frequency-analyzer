"""Command-line entry point: python -m frequency_analyzer <file.wav>."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from frequency_analyzer.analysis import compute_spectrum, dominant_frequency
from frequency_analyzer.audio import load_wav
from frequency_analyzer.plots import plot_spectrum


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Read the path of the WAV file from the command line."""
    parser = argparse.ArgumentParser(
        prog="python -m frequency_analyzer",
        description="Show the frequency spectrum of a WAV file.",
    )
    parser.add_argument("path", type=Path, help="path of the WAV file to analyze")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Analyze a WAV file, print its dominant frequency and show its spectrum."""
    args = parse_args(argv)
    samples, sample_rate = load_wav(args.path)
    frequencies, magnitudes = compute_spectrum(samples, sample_rate)
    dominant = dominant_frequency(frequencies, magnitudes)
    print(f"Dominant frequency: {dominant:.1f} Hz")

    figure, axes = plt.subplots()
    figure.canvas.manager.set_window_title(args.path.name)
    plot_spectrum(axes, frequencies, magnitudes)
    plt.show()


if __name__ == "__main__":
    main()

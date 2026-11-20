"""Command-line entry point: python -m frequency_analyzer [file.wav]."""

import argparse
import sys
import tkinter as tk
from pathlib import Path

from frequency_analyzer.audio import AudioFileError
from frequency_analyzer.gui import AnalyzerWindow

PROG = "python -m frequency_analyzer"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Read the optional path of a WAV file from the command line."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Show the waveform, spectrum and spectrogram of a WAV file.",
    )
    parser.add_argument(
        "path", nargs="?", type=Path, help="path of a WAV file to open at start"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Open the window, with the given WAV file if there is one.

    If the file cannot be analyzed, print the reason and exit with code 1
    without showing the window.
    """
    args = parse_args(argv)
    root = tk.Tk()
    window = AnalyzerWindow(root)
    if args.path is not None:
        try:
            window.show_file(args.path)
        except AudioFileError as error:
            root.destroy()
            print(f"{PROG}: error: {error}", file=sys.stderr)
            sys.exit(1)
    root.mainloop()


if __name__ == "__main__":
    main()

"""Desktop window that shows the plots of a WAV file."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from frequency_analyzer.analysis import (
    SEGMENT_DURATION,
    compute_spectrogram,
    compute_spectrum,
    dominant_frequency,
    to_decibels,
)
from frequency_analyzer.audio import AudioFileError, load_wav
from frequency_analyzer.plots import plot_spectrogram, plot_spectrum, plot_waveform

APP_NAME = "Frequency Analyzer"
NO_FILE_TEXT = "No file loaded"
EMPTY_HINT = "Open a WAV file to see its waveform, spectrum and spectrogram"


def draw_analysis(
    figure: Figure, samples: np.ndarray, sample_rate: int, decibels: bool = False
) -> None:
    """Draw the waveform, the spectrum and the spectrogram on the given figure.

    The waveform and the spectrum are side by side, and the spectrogram is below
    them across the whole width. With decibels=True, the spectrum and the
    spectrogram are drawn in dB. Anything already on the figure is removed
    first, so that the same figure can show one file after another. Everything is
    computed before that, so that an error leaves the figure as it was.
    """
    frequencies, magnitudes = compute_spectrum(samples, sample_rate)
    times, segment_frequencies, segments = compute_spectrogram(samples, sample_rate)
    if decibels:
        magnitudes = to_decibels(magnitudes)
        segments = to_decibels(segments)

    figure.clear()
    grid = figure.add_gridspec(2, 2)
    waveform_axes = figure.add_subplot(grid[0, 0])
    spectrum_axes = figure.add_subplot(grid[0, 1])
    spectrogram_axes = figure.add_subplot(grid[1, :])

    plot_waveform(waveform_axes, samples, sample_rate)
    plot_spectrum(spectrum_axes, frequencies, magnitudes, decibels)
    plot_spectrogram(spectrogram_axes, times, segment_frequencies, segments, decibels)


class NavigationToolbar(NavigationToolbar2Tk):
    """The matplotlib navigation toolbar without the Subplots button.

    The figure places its plots by itself (constrained layout), so the sliders
    of the Subplots button would change nothing.
    """

    toolitems = [
        item for item in NavigationToolbar2Tk.toolitems if item[0] != "Subplots"
    ]


class AnalyzerWindow:
    """A figure in the given tkinter window, below a bar for opening a WAV file."""

    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self.root = root
        self.root.title(APP_NAME)

        bar = tk.Frame(root, padx=10, pady=8)
        bar.pack(fill=tk.X)
        self.open_button = tk.Button(
            bar, text="Open WAV file…", command=self.choose_file
        )
        self.open_button.pack(side=tk.LEFT)
        self.file_label = tk.Label(bar, text=NO_FILE_TEXT, padx=12)
        self.file_label.pack(side=tk.LEFT)
        self.decibels = tk.BooleanVar(value=False)
        self.decibels_button = tk.Checkbutton(
            bar, text="Decibels", variable=self.decibels, command=self.redraw
        )
        self.decibels_button.pack(side=tk.LEFT)
        self.frequency_label = tk.Label(bar, padx=12)
        self.frequency_label.pack(side=tk.RIGHT)

        self.figure = Figure(figsize=(11, 7.5), layout="constrained")
        self.figure.text(0.5, 0.5, EMPTY_HINT, ha="center", va="center")
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.toolbar = NavigationToolbar(self.canvas, root, pack_toolbar=False)
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.samples: np.ndarray | None = None
        self.sample_rate = 0

    def choose_file(self) -> None:
        """Ask for a WAV file in a dialog and show it, unless it is cancelled.

        A file that cannot be analyzed is reported in an error dialog, and the
        window keeps the current file.
        """
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Open a WAV file",
            filetypes=[("WAV files", "*.wav")],
        )
        if not path:
            return
        try:
            self.show_file(path)
        except AudioFileError as error:
            messagebox.showerror("Cannot open the file", str(error), parent=self.root)

    def show_file(self, path: str | Path) -> None:
        """Load a WAV file, draw its plots and show its name and dominant frequency.

        Raises AudioFileError, before changing anything in the window, if the file
        cannot be read or is shorter than one spectrogram segment (50 ms).
        """
        samples, sample_rate = load_wav(path)
        duration = len(samples) / sample_rate
        if duration < SEGMENT_DURATION:
            raise AudioFileError(
                f"{path} is too short to analyze: it lasts {int(duration * 1000)} ms, "
                f"and at least {SEGMENT_DURATION * 1000:.0f} ms are needed."
            )
        self.samples, self.sample_rate = samples, sample_rate
        self.redraw()
        name = Path(path).name
        self.file_label.configure(text=name)
        self.root.title(f"{name} - {APP_NAME}")
        dominant = dominant_frequency(*compute_spectrum(samples, sample_rate))
        value = "none (silence)" if dominant is None else f"{dominant:.1f} Hz"
        self.frequency_label.configure(text=f"Dominant frequency: {value}")

    def redraw(self) -> None:
        """Draw the plots of the current file, in decibels if the box is ticked."""
        if self.samples is None:
            return
        draw_analysis(self.figure, self.samples, self.sample_rate, self.decibels.get())
        self.canvas.draw()

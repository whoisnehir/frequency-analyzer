"""Desktop window that shows the plots of a WAV file."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from frequency_analyzer.analysis import (
    compute_spectrogram,
    compute_spectrum,
    dominant_frequency,
)
from frequency_analyzer.audio import load_wav
from frequency_analyzer.plots import plot_spectrogram, plot_spectrum, plot_waveform

APP_NAME = "Frequency Analyzer"
NO_FILE_TEXT = "No file loaded"
EMPTY_HINT = "Open a WAV file to see its waveform, spectrum and spectrogram"


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
        self.frequency_label = tk.Label(bar, padx=12)
        self.frequency_label.pack(side=tk.RIGHT)

        self.figure = Figure(figsize=(11, 7.5), layout="constrained")
        self.figure.text(0.5, 0.5, EMPTY_HINT, ha="center", va="center")
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.toolbar = NavigationToolbar(self.canvas, root, pack_toolbar=False)
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def choose_file(self) -> None:
        """Ask for a WAV file in a dialog and show it, unless it is cancelled."""
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Open a WAV file",
            filetypes=[("WAV files", "*.wav")],
        )
        if path:
            self.show_file(path)

    def show_file(self, path: str | Path) -> None:
        """Load a WAV file, draw its plots and show its name and dominant frequency."""
        samples, sample_rate = load_wav(path)
        draw_analysis(self.figure, samples, sample_rate)
        self.canvas.draw()
        name = Path(path).name
        self.file_label.configure(text=name)
        self.root.title(f"{name} - {APP_NAME}")
        dominant = dominant_frequency(*compute_spectrum(samples, sample_rate))
        self.frequency_label.configure(text=f"Dominant frequency: {dominant:.1f} Hz")

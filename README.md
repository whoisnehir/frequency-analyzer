# Frequency Analyzer

[![CI](https://github.com/whoisnehir/frequency-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/whoisnehir/frequency-analyzer/actions/workflows/ci.yml)

> **Status:** work in progress. Progress is tracked on the [project board](https://github.com/users/whoisnehir/projects/3).

A desktop application that shows which frequencies an audio recording contains. It loads a WAV file, computes its spectrum with the Fast Fourier Transform (FFT) and displays the waveform, the frequency spectrum and the spectrogram in a dark-themed interface.

## Planned features

- Load a WAV file
- Plot the waveform (amplitude over time)
- Compute the FFT and plot the frequency spectrum
- Plot the spectrogram (how the frequencies change over time)
- Show the dominant frequency
- Display the spectrum in decibels (dB)
- Show clear error messages for invalid or unsupported files
- Dark-themed desktop interface built with tkinter

## Tech stack

- **Python 3**
- **SciPy**: reading WAV files, FFT, spectrogram
- **NumPy**: numerical arrays
- **matplotlib**: plots
- **tkinter**: desktop interface
- **ruff**, **pytest** and **GitHub Actions**: formatting, linting, tests and continuous integration

## Installation

Requires Python 3.13 or newer.

```bash
git clone https://github.com/whoisnehir/frequency-analyzer.git
cd frequency-analyzer
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux and macOS
source .venv/bin/activate
```

Install the project with its development tools:

```bash
python -m pip install -e ".[dev]"
```

On Linux, the window also needs tkinter, which some distributions package separately (for example `sudo apt install python3-tk` on Debian and Ubuntu).

## Usage

Generate the test tones, then open the analyzer:

```bash
python scripts/generate_tones.py
python -m frequency_analyzer
```

The script writes four two-second WAV files into `samples/`:

| File                                | Content                                         |
| ----------------------------------- | ----------------------------------------------- |
| `tone_440hz.wav`                    | a 440 Hz tone                                   |
| `mix_300_1000_2500hz.wav`           | a mix of 300, 1000 and 2500 Hz                  |
| `stereo_440hz_left_660hz_right.wav` | 440 Hz on the left channel, 660 Hz on the right |
| `notes_880_440_1100_660hz.wav`      | four tones in a row: 880, 440, 1100 and 660 Hz  |

Choose a file with the **Open WAV file…** button, or open one directly from the command line:

```bash
python -m frequency_analyzer samples/notes_880_440_1100_660hz.wav
```

The bar at the top shows the name of the file and its dominant frequency (`Dominant frequency: 440.0 Hz`). Below it, the waveform and the frequency spectrum are side by side, and the spectrogram is under them. The spectrogram shows how the frequencies change over time: try it on `notes_880_440_1100_660hz.wav` to see the four tones in order. The toolbar at the bottom zooms into the plots, pans them and saves them as an image, and shows the time, frequency and amplitude under the mouse pointer. Other WAV files, mono or stereo, are analyzed the same way. `python -m frequency_analyzer --help` shows the usage.

## Development

The same checks run on every pull request with GitHub Actions, where the window tests use a virtual display (`xvfb-run pytest`):

```bash
ruff format --check .
ruff check .
pytest
```

## Progress

- [x] [M1 Setup](https://github.com/whoisnehir/frequency-analyzer/milestone/1): README, issue template, project structure, ruff, pytest, GitHub Actions
- [x] [M2 Core analysis](https://github.com/whoisnehir/frequency-analyzer/milestone/2): load a WAV file, compute the FFT, plot the spectrum
- [x] [M3 Full plots](https://github.com/whoisnehir/frequency-analyzer/milestone/3): waveform and spectrogram
- [ ] [M4 GUI](https://github.com/whoisnehir/frequency-analyzer/milestone/4): tkinter window, file picker, embedded plots, dominant frequency, dark theme
- [ ] [M5 Polish](https://github.com/whoisnehir/frequency-analyzer/milestone/5): dB scale, error handling
- [ ] [M6 Release](https://github.com/whoisnehir/frequency-analyzer/milestone/6): final code review, documentation and the v1.0.0 release

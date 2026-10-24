# Frequency Analyzer

> **Status:** work in progress. Progress is tracked on the [project board](https://github.com/users/whoisnehir/projects/3).

A desktop application that shows which frequencies an audio recording contains. It loads a WAV file, computes its spectrum with the Fast Fourier Transform (FFT) and displays the waveform, the frequency spectrum and the spectrogram in a dark-themed interface.

Built as the lab project for the Audio Signal Processing course (*Prelucrarea semnalelor auditive*) at Politehnica University of Timișoara.

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

## Progress

- [ ] [M1 Setup](https://github.com/whoisnehir/frequency-analyzer/milestone/1): README, issue template, project structure, ruff, pytest, GitHub Actions
- [ ] [M2 Core analysis](https://github.com/whoisnehir/frequency-analyzer/milestone/2): load a WAV file, compute the FFT, plot the spectrum
- [ ] [M3 Full plots](https://github.com/whoisnehir/frequency-analyzer/milestone/3): waveform and spectrogram
- [ ] [M4 GUI](https://github.com/whoisnehir/frequency-analyzer/milestone/4): tkinter window, file picker, embedded plots, dark theme
- [ ] [M5 Polish](https://github.com/whoisnehir/frequency-analyzer/milestone/5): dominant frequency, dB scale, error handling
- [ ] [M6 Presentation prep](https://github.com/whoisnehir/frequency-analyzer/milestone/6): review of the code and the course concepts
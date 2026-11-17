"""Write WAV files with known tones into samples/, for trying the analyzer."""

from pathlib import Path

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100
DURATION = 2.0
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "samples"


def sine(frequency: float, amplitude: float) -> np.ndarray:
    """Return a sine wave of the given frequency, from -amplitude to amplitude."""
    time = np.arange(int(SAMPLE_RATE * DURATION)) / SAMPLE_RATE
    return amplitude * np.sin(2 * np.pi * frequency * time)


def to_int16(signal: np.ndarray) -> np.ndarray:
    """Convert a signal between -1 and 1 to 16-bit integer samples."""
    if np.abs(signal).max() >= 1:
        raise ValueError("The signal must stay below full scale.")
    return np.round(signal * 32767).astype(np.int16)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    tones = {
        "tone_440hz.wav": sine(440, 0.5),
        "mix_300_1000_2500hz.wav": sine(300, 0.4) + sine(1000, 0.25) + sine(2500, 0.15),
        "stereo_440hz_left_660hz_right.wav": np.column_stack(
            [sine(440, 0.5), sine(660, 0.3)]
        ),
    }
    for name, signal in tones.items():
        path = OUTPUT_DIR / name
        wavfile.write(path, SAMPLE_RATE, to_int16(signal))
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()

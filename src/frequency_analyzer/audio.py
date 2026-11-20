"""Reading WAV files into samples that are ready for analysis."""

import warnings
from pathlib import Path

import numpy as np
from scipy.io import wavfile


class AudioFileError(Exception):
    """A file that cannot be read or analyzed, with a message for the user."""


def load_wav(path: str | Path) -> tuple[np.ndarray, int]:
    """Read a WAV file as a single channel of samples between -1 and 1.

    Stereo (multi-channel) files are averaged into one channel, and integer
    samples are scaled by the largest value of their type.

    Returns the samples as a 1-D array of floats and the sample rate in Hz.
    Raises AudioFileError if the file does not exist, cannot be opened or is
    not a WAV file that can be read.
    """
    try:
        with warnings.catch_warnings():
            # Some WAV files contain metadata chunks that SciPy skips with a warning.
            warnings.simplefilter("ignore", wavfile.WavFileWarning)
            sample_rate, data = wavfile.read(path)
    except FileNotFoundError as error:
        raise AudioFileError(f"{path} does not exist.") from error
    except OSError as error:
        raise AudioFileError(f"{path} cannot be opened: {error.strerror}.") from error
    except Exception as error:
        # SciPy raises many kinds of errors for files that are not valid WAV
        # files (ValueError, struct.error and others), so any other error while
        # reading means that the file cannot be read as a WAV file.
        raise AudioFileError(f"{path} is not a WAV file that can be read.") from error

    samples = _to_float(data)
    if samples.ndim == 2:
        samples = samples.mean(axis=1)
    return samples, sample_rate


def _to_float(data: np.ndarray) -> np.ndarray:
    """Convert raw WAV samples to floats between -1 and 1."""
    if data.dtype == np.uint8:
        # 8-bit WAV samples are unsigned: 128 is silence.
        return (data.astype(np.float64) - 128) / 128
    if np.issubdtype(data.dtype, np.integer):
        full_scale = np.iinfo(data.dtype).max + 1
        return data.astype(np.float64) / full_scale
    return data.astype(np.float64)

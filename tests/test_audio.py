"""Tests for reading WAV files."""

import warnings

import numpy as np
import pytest
from scipy.io import wavfile

from frequency_analyzer.audio import AudioFileError, load_wav


def test_mono_16_bit_file_is_scaled_to_floats(tmp_path):
    path = tmp_path / "mono.wav"
    data = np.array([0, 16384, -32768, 32767], dtype=np.int16)
    wavfile.write(path, 8000, data)

    samples, sample_rate = load_wav(path)

    assert sample_rate == 8000
    assert samples.dtype == np.float64
    assert samples.ndim == 1
    np.testing.assert_allclose(samples, [0.0, 0.5, -1.0, 32767 / 32768])


def test_stereo_file_is_averaged_into_one_channel(tmp_path):
    path = tmp_path / "stereo.wav"
    data = np.array([[16384, 0], [0, -16384], [32767, 32767]], dtype=np.int16)
    wavfile.write(path, 8000, data)

    samples, _ = load_wav(path)

    assert samples.ndim == 1
    np.testing.assert_allclose(samples, [0.25, -0.25, 32767 / 32768])


def test_float_file_keeps_its_values(tmp_path):
    path = tmp_path / "float.wav"
    data = np.array([0.5, -0.25, 0.0], dtype=np.float32)
    wavfile.write(path, 8000, data)

    samples, _ = load_wav(path)

    np.testing.assert_allclose(samples, [0.5, -0.25, 0.0])


def test_8_bit_file_is_centered_and_scaled(tmp_path):
    path = tmp_path / "eight_bit.wav"
    data = np.array([128, 192, 0], dtype=np.uint8)
    wavfile.write(path, 8000, data)

    samples, _ = load_wav(path)

    np.testing.assert_allclose(samples, [0.0, 0.5, -1.0])


def test_file_with_metadata_chunk_is_read_without_warnings(tmp_path):
    path = tmp_path / "metadata.wav"
    wavfile.write(path, 8000, np.array([0, 16384], dtype=np.int16))
    _append_unknown_chunk(path)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        samples, sample_rate = load_wav(path)

    assert sample_rate == 8000
    np.testing.assert_allclose(samples, [0.0, 0.5])


def _append_unknown_chunk(path):
    """Add a chunk that SciPy does not understand, as in files with metadata."""
    content = bytearray(path.read_bytes())
    content += b"meta" + (4).to_bytes(4, "little") + b"info"
    content[4:8] = (len(content) - 8).to_bytes(4, "little")
    path.write_bytes(bytes(content))


def test_missing_file_is_reported_with_its_path(tmp_path):
    path = tmp_path / "missing.wav"

    with pytest.raises(AudioFileError, match="does not exist") as error_info:
        load_wav(path)

    assert str(error_info.value) == f"{path} does not exist."
    assert isinstance(error_info.value.__cause__, FileNotFoundError)


@pytest.mark.parametrize(
    "content",
    [b"", b"hello", b"RIFF" + bytes(100), b"RIFF\x00\x00\x00\x00WAVEfmt "],
    ids=["empty", "text", "riff-without-wave", "cut-in-header"],
)
def test_file_that_is_not_a_wav_file_is_reported(tmp_path, content):
    path = tmp_path / "not_a_wav.wav"
    path.write_bytes(content)

    with pytest.raises(AudioFileError) as error_info:
        load_wav(path)

    assert str(error_info.value) == f"{path} is not a WAV file that can be read."


def test_folder_cannot_be_opened(tmp_path):
    folder = tmp_path / "folder.wav"
    folder.mkdir()

    with pytest.raises(AudioFileError, match="cannot be opened: "):
        load_wav(folder)

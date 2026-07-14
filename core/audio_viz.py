# -*- coding: utf-8 -*-
"""오디오 음향 시각화 생성 (CLAUDE.md 4-1-C 참고).

업로드 시 1회 생성 후 PNG로 캐시. matplotlib 사용, 한글 라벨 지원을 위해
설치된 한글 폰트가 있으면 사용하고 없으면 영문 라벨로 폴백.
"""

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import librosa
import librosa.display

_KOREAN_FONT_CANDIDATES = [
    "AppleGothic", "Apple SD Gothic Neo", "Malgun Gothic", "NanumGothic", "NanumBarunGothic",
]


def _setup_korean_font():
    available = {f.name for f in fm.fontManager.ttflist}
    for name in _KOREAN_FONT_CANDIDATES:
        if name in available:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return True
    return False


_HAS_KOREAN_FONT = _setup_korean_font()


def _label(ko: str, en: str) -> str:
    return ko if _HAS_KOREAN_FONT else en


def load_audio(file_path, sr=22050):
    y, sr = librosa.load(str(file_path), sr=sr, mono=True)
    return y, sr


def generate_waveform_png(y, sr, out_path):
    fig, ax = plt.subplots(figsize=(8, 2.5))
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#3b6fb6")
    ax.set_title(_label("파형 (Waveform)", "Waveform"))
    ax.set_xlabel(_label("시간 (초)", "Time (s)"))
    ax.set_ylabel(_label("진폭", "Amplitude"))
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def generate_melspectrogram_png(y, sr, out_path):
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    fig, ax = plt.subplots(figsize=(8, 3))
    img = librosa.display.specshow(
        mel_db, sr=sr, x_axis="time", y_axis="mel", ax=ax, cmap="magma"
    )
    ax.set_title(_label("멜 스펙트로그램", "Mel Spectrogram"))
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def compute_f0(y, sr, fmin=80, fmax=4000):
    """librosa.pyin으로 F0 궤적 추출. 경보음 기본 주파수 추적 목적."""
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y, fmin=fmin, fmax=fmax, sr=sr
    )
    times = librosa.times_like(f0, sr=sr)
    return times, f0, voiced_flag


def generate_f0_png(y, sr, out_path):
    times, f0, voiced_flag = compute_f0(y, sr)
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.plot(times, f0, color="#c0392b", linewidth=1.5)
    ax.set_title(_label("피치(F0) 궤적", "F0 Contour"))
    ax.set_xlabel(_label("시간 (초)", "Time (s)"))
    ax.set_ylabel(_label("주파수 (Hz)", "Frequency (Hz)"))
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return times, f0


def generate_rms_png(y, sr, out_path):
    rms = librosa.feature.rms(y=y)[0]
    times = librosa.times_like(rms, sr=sr)
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.plot(times, rms, color="#27ae60", linewidth=1.5)
    ax.set_title(_label("RMS 에너지 (떨림/변동성 지표)", "RMS Energy (tremor proxy)"))
    ax.set_xlabel(_label("시간 (초)", "Time (s)"))
    ax.set_ylabel("RMS")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return times, rms


def compute_tremor_stats(f0):
    """F0 표준편차 기반 '떨림' 1차 지표."""
    valid = f0[~np.isnan(f0)] if f0 is not None else np.array([])
    if len(valid) == 0:
        return {"f0_mean": None, "f0_std": None, "voiced_ratio": 0.0}
    return {
        "f0_mean": float(np.mean(valid)),
        "f0_std": float(np.std(valid)),
        "voiced_ratio": float(len(valid) / len(f0)) if f0 is not None and len(f0) else 0.0,
    }


def generate_all_visualizations_bytes(file_path):
    """업로드된 오디오 파일(로컬 임시 경로)에 대해 4종 시각화를 생성해 PNG bytes로 반환.

    Drive 기반 저장소에서는 로컬에 캐시 파일을 남기지 않고, 생성된 bytes를
    바로 storage.upload_bytes()로 Drive에 올리는 흐름으로 사용한다.
    """
    y, sr = load_audio(file_path)

    waveform_buf = io.BytesIO()
    melspec_buf = io.BytesIO()
    f0_buf = io.BytesIO()
    rms_buf = io.BytesIO()

    generate_waveform_png(y, sr, waveform_buf)
    generate_melspectrogram_png(y, sr, melspec_buf)
    _, f0 = generate_f0_png(y, sr, f0_buf)
    generate_rms_png(y, sr, rms_buf)

    tremor_stats = compute_tremor_stats(f0)
    clip_length_sec = len(y) / sr

    return {
        "waveform": waveform_buf.getvalue(),
        "melspec": melspec_buf.getvalue(),
        "f0": f0_buf.getvalue(),
        "rms": rms_buf.getvalue(),
        "tremor_stats": tremor_stats,
        "clip_length_sec": clip_length_sec,
    }

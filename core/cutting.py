# -*- coding: utf-8 -*-
"""원본 비상 오디오 자동 커팅 (2차 목표, CLAUDE.md 4-1-B 참고).

pydub 기반. 긴 원본 녹음을 TARGET_CLIP_LENGTH_SEC 단위로 잘라
서버 커팅용 임시 결과를 반환한다. 현재는 단순 고정 길이 슬라이싱만 구현.
(경보음 자동 탐지를 통한 스마트 커팅은 추후 확장)
"""

from pydub import AudioSegment

from core.config import TARGET_CLIP_LENGTH_SEC


def cut_fixed_length(input_path, segment_sec: int = TARGET_CLIP_LENGTH_SEC):
    """input_path의 오디오를 segment_sec(초) 단위로 잘라 AudioSegment 리스트 반환.
    마지막 조각이 segment_sec보다 짧으면 버린다 (5~6초 기준 미달 방지).
    """
    audio = AudioSegment.from_file(str(input_path))
    segment_ms = segment_sec * 1000
    total_ms = len(audio)

    segments = []
    start = 0
    while start + segment_ms <= total_ms:
        segments.append(audio[start:start + segment_ms])
        start += segment_ms
    return segments


def export_segments(segments, out_dir, stem_prefix):
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, seg in enumerate(segments, start=1):
        path = out_dir / f"{stem_prefix}_cut{i:02d}.wav"
        seg.export(str(path), format="wav")
        paths.append(path)
    return paths

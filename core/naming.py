# -*- coding: utf-8 -*-
"""파일명 규칙 생성 (CLAUDE.md 3장 참고).

장소_차종_방향_거리_기능없음_벽면없음_주차위치_NNN.wav
조건 + 기능/벽면 라벨을 언더바로 연결하고, 마지막 3자리는 동일 조합 내 순번.
"""

from core.config import FILENAME_FIELD_ORDER


def build_stem(labels: dict) -> str:
    """확장자/순번을 제외한 파일명 stem 생성.

    labels: FILENAME_FIELD_ORDER에 포함된 모든 키를 갖는 dict
    """
    parts = [str(labels[field]) for field in FILENAME_FIELD_ORDER]
    return "_".join(parts)


def build_filename(labels: dict, seq: int, ext: str = "wav") -> str:
    stem = build_stem(labels)
    return f"{stem}_{seq:03d}.{ext}"

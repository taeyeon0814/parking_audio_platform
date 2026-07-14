# -*- coding: utf-8 -*-
"""
실험 조건/라벨 정의 (single source of truth).

CLAUDE.md 3장 참고: CONDITIONS(조건)와 EXTRA_LABELS(추가 라벨)는 교수님 피드백에 따른
설계 결정으로 명확히 구분되어 있음. CONDITIONS는 커버리지(96조건×30회) 계산 대상이고,
EXTRA_LABELS는 조건화에서 제외된 부산물 라벨(기능없음/벽면없음 등)이다.
절대로 이 둘을 합치거나 서로 옮기지 말 것.
"""

from collections import OrderedDict
import itertools

# ---------------------------------------------------------------------------
# 조건 (CONDITIONS) — 커버리지 계산 대상. 총 4x3x2x2x2 = 96개 조합.
# key: 내부 필드명 / value: (표시 라벨, 선택지 목록)
# ---------------------------------------------------------------------------
CONDITIONS = OrderedDict(
    [
        ("direction", ("방향", ["전", "후", "좌", "우"])),
        ("distance", ("거리", ["근거리", "중거리", "원거리"])),
        ("vehicle_type", ("차종", ["세단", "기타"])),
        ("place", ("장소", ["백화점", "마트"])),
        ("parking_position", ("주차위치", ["전방주차", "후방주차"])),
    ]
)

# 조건당 목표 반복 횟수 (중심극한정리 근거, n >= 30)
TARGET_PER_CONDITION = 30

# 목표 클립 길이(초). 5~6초 허용, 기본 6초.
TARGET_CLIP_LENGTH_SEC = 6
MIN_CLIP_LENGTH_SEC = 5
MAX_CLIP_LENGTH_SEC = 6

# ---------------------------------------------------------------------------
# 추가 라벨 (EXTRA_LABELS) — 조건화 제외, 클립마다 기록만 하는 부산물 라벨.
# ---------------------------------------------------------------------------
EXTRA_LABELS = OrderedDict(
    [
        ("floor", ("층", ["B1", "B2", "B3", "기타"])),
        ("zone", ("구역", None)),  # 자유 텍스트
        ("no_facility_nearby", ("기능없음", ["있음", "없음"])),
        ("no_wall_nearby", ("벽면없음", ["있음", "없음"])),
        ("background_noise", ("배경잡음", None)),  # 자유 텍스트
    ]
)

# 파일명에 사용되는 필드 순서 (CLAUDE.md 3장 파일명 규칙 참고)
# 장소_차종_방향_거리_기능없음_벽면없음_주차위치_NNN.wav
FILENAME_FIELD_ORDER = [
    "place",
    "vehicle_type",
    "direction",
    "distance",
    "no_facility_nearby",
    "no_wall_nearby",
    "parking_position",
]


def condition_field_names():
    """CONDITIONS의 내부 필드명 리스트."""
    return list(CONDITIONS.keys())


def all_condition_combinations():
    """
    가능한 모든 조건 조합(96개)을 dict 리스트로 반환.
    순서는 CONDITIONS에 정의된 순서를 따름.
    """
    fields = condition_field_names()
    choices = [CONDITIONS[f][1] for f in fields]
    combos = []
    for values in itertools.product(*choices):
        combos.append(dict(zip(fields, values)))
    return combos


def total_condition_count():
    return len(all_condition_combinations())


def total_target_clip_count():
    return total_condition_count() * TARGET_PER_CONDITION


def condition_label(field_name):
    """내부 필드명 -> 한글 표시 라벨."""
    return CONDITIONS[field_name][0]


def extra_label_label(field_name):
    return EXTRA_LABELS[field_name][0]

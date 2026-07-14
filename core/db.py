# -*- coding: utf-8 -*-
"""메타데이터 저장소. Google Sheets를 DB처럼 사용한다 (CLAUDE.md 4-2 설계 결정 반영).

clips 시트: 조건/추가라벨 + Drive 파일ID(오디오, 시각화 4종)
documents 시트: 자료실 문서 메타 + Drive 파일ID

성능을 위해 조회 결과는 짧은 TTL로 캐시하고(st.cache_data), 쓰기(append) 직후
캐시를 무효화한다. 조건당 30회 x 96조건 = 2,880행 규모에서는 매번 전체를
읽어도 충분히 빠르다.
"""

from datetime import datetime

import streamlit as st

from core.config import condition_field_names, EXTRA_LABELS
from core.gcp_auth import get_gspread_client, spreadsheet_id

CONDITION_FIELDS = condition_field_names()
EXTRA_FIELDS = list(EXTRA_LABELS.keys())

CLIPS_SHEET = "clips"
DOCUMENTS_SHEET = "documents"

CLIPS_COLUMNS = (
    ["clip_id"]
    + CONDITION_FIELDS
    + EXTRA_FIELDS
    + [
        "uploader_name",
        "original_filename",
        "stored_filename",
        "drive_audio_file_id",
        "clip_length_sec",
        "uploaded_at",
        "viz_waveform_file_id",
        "viz_melspec_file_id",
        "viz_f0_file_id",
        "viz_rms_file_id",
    ]
)

DOCUMENTS_COLUMNS = [
    "doc_id",
    "title",
    "original_filename",
    "drive_file_id",
    "uploader_name",
    "uploaded_at",
]


def _spreadsheet():
    gc = get_gspread_client()
    return gc.open_by_key(spreadsheet_id())


def _get_or_create_worksheet(name: str, columns: list):
    ss = _spreadsheet()
    try:
        ws = ss.worksheet(name)
    except Exception:
        ws = ss.add_worksheet(title=name, rows=2000, cols=len(columns) + 2)
        ws.append_row(columns)
    return ws


def init_db():
    _get_or_create_worksheet(CLIPS_SHEET, CLIPS_COLUMNS)
    _get_or_create_worksheet(DOCUMENTS_SHEET, DOCUMENTS_COLUMNS)


@st.cache_data(ttl=15, show_spinner=False)
def fetch_all_clips():
    ws = _get_or_create_worksheet(CLIPS_SHEET, CLIPS_COLUMNS)
    return ws.get_all_records()


def next_seq_for_combo(combo: dict) -> int:
    """동일 조건 조합 내 다음 순번(1부터) 반환."""
    records = fetch_all_clips()
    cnt = 0
    for r in records:
        if all(str(r.get(f, "")) == str(combo[f]) for f in CONDITION_FIELDS):
            cnt += 1
    return cnt + 1


def insert_clip(
    labels: dict,
    uploader_name,
    original_filename,
    stored_filename,
    drive_audio_file_id,
    clip_length_sec,
    viz_file_ids=None,
):
    viz_file_ids = viz_file_ids or {}
    ws = _get_or_create_worksheet(CLIPS_SHEET, CLIPS_COLUMNS)
    clip_id = len(ws.get_all_values()) - 1 + 1  # 헤더 제외 행수 + 1

    row = [clip_id]
    for f in CONDITION_FIELDS + EXTRA_FIELDS:
        row.append(labels.get(f, ""))
    row += [
        uploader_name,
        original_filename,
        stored_filename,
        drive_audio_file_id,
        clip_length_sec,
        datetime.now().isoformat(timespec="seconds"),
        viz_file_ids.get("waveform", ""),
        viz_file_ids.get("melspec", ""),
        viz_file_ids.get("f0", ""),
        viz_file_ids.get("rms", ""),
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")
    fetch_all_clips.clear()
    return clip_id


def fetch_clip(clip_id: int):
    for r in fetch_all_clips():
        if str(r.get("clip_id")) == str(clip_id):
            return r
    return None


def count_by_condition_combo():
    """조건 조합별 수집 개수를 dict[tuple(values)] -> count 형태로 반환."""
    result = {}
    for r in fetch_all_clips():
        key = tuple(r.get(f) for f in CONDITION_FIELDS)
        result[key] = result.get(key, 0) + 1
    return result


def insert_document(title, original_filename, drive_file_id, uploader_name):
    ws = _get_or_create_worksheet(DOCUMENTS_SHEET, DOCUMENTS_COLUMNS)
    doc_id = len(ws.get_all_values()) - 1 + 1

    ws.append_row(
        [
            doc_id,
            title,
            original_filename,
            drive_file_id,
            uploader_name,
            datetime.now().isoformat(timespec="seconds"),
        ],
        value_input_option="USER_ENTERED",
    )
    fetch_all_documents.clear()
    return doc_id


@st.cache_data(ttl=15, show_spinner=False)
def fetch_all_documents():
    ws = _get_or_create_worksheet(DOCUMENTS_SHEET, DOCUMENTS_COLUMNS)
    return ws.get_all_records()

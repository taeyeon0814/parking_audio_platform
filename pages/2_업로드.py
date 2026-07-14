# -*- coding: utf-8 -*-
"""오디오 업로드 + 라벨링 (CLAUDE.md 4-1-B).

Google Drive에 오디오/시각화를 업로드하고, 메타데이터는 Google Sheets에 기록한다.
"""

import tempfile
from pathlib import Path

import soundfile as sf
import streamlit as st

from core.config import CONDITIONS, EXTRA_LABELS, condition_field_names
from core.naming import build_filename
from core.db import insert_clip, next_seq_for_combo
from core.storage import upload_bytes, FOLDER_AUDIO, FOLDER_VIZ
from core.audio_viz import generate_all_visualizations_bytes
from core.ui_common import require_auth_and_setup

st.set_page_config(page_title="업로드", page_icon="⬆️", layout="wide")

require_auth_and_setup()

st.title("⬆️ 오디오 업로드 + 라벨링")
st.caption("조건 5개 + 추가 라벨을 선택한 후 파일을 업로드하면, 파일명 규칙에 따라 자동으로 이름이 지정되고 "
           "Google Drive에 저장 + 시각화가 생성됩니다.")

uploader_name = st.text_input("업로더 이름")

st.subheader("실험 조건")
cond_values = {}
cond_cols = st.columns(len(CONDITIONS))
for col, (field, (label, options)) in zip(cond_cols, CONDITIONS.items()):
    cond_values[field] = col.selectbox(label, options, key=f"cond_{field}")

st.subheader("추가 라벨 (조건 외 부산물 정보)")
extra_values = {}
extra_cols = st.columns(len(EXTRA_LABELS))
for col, (field, (label, options)) in zip(extra_cols, EXTRA_LABELS.items()):
    if options is None:
        extra_values[field] = col.text_input(label, key=f"extra_{field}")
    else:
        extra_values[field] = col.selectbox(label, options, key=f"extra_{field}")

st.subheader("오디오 파일")
uploaded_file = st.file_uploader("WAV/MP3 파일 업로드", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file)

if st.button("업로드 및 저장", type="primary", disabled=uploaded_file is None):
    if not uploader_name.strip():
        st.error("업로더 이름을 입력해주세요.")
        st.stop()

    all_labels = {**cond_values, **extra_values}
    fields = condition_field_names()
    combo = {f: cond_values[f] for f in fields}

    ext = Path(uploaded_file.name).suffix.lstrip(".").lower() or "wav"
    raw_bytes = uploaded_file.getvalue()

    with st.spinner("오디오 분석 및 시각화 생성 중..."):
        # librosa/soundfile은 파일 경로가 필요하므로 임시 파일에 잠깐 기록 후 처리
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(raw_bytes)
            tmp_path = Path(tmp.name)

        try:
            info = sf.info(str(tmp_path))
            clip_length_sec = info.frames / info.samplerate
        except Exception:
            clip_length_sec = None

        try:
            viz_result = generate_all_visualizations_bytes(tmp_path)
            if clip_length_sec is None:
                clip_length_sec = viz_result["clip_length_sec"]
        except Exception as e:
            st.error(f"시각화 생성 중 오류가 발생했습니다: {e}")
            tmp_path.unlink(missing_ok=True)
            st.stop()
        finally:
            tmp_path.unlink(missing_ok=True)

    with st.spinner("Google Drive 업로드 및 Google Sheets 기록 중..."):
        seq = next_seq_for_combo(combo)
        stored_filename = build_filename(all_labels, seq, ext=ext)
        stem = Path(stored_filename).stem

        mime_map = {"wav": "audio/wav", "mp3": "audio/mpeg", "m4a": "audio/mp4"}
        audio_file_id = upload_bytes(
            raw_bytes, stored_filename, mime_map.get(ext, "application/octet-stream"), FOLDER_AUDIO
        )

        viz_file_ids = {
            "waveform": upload_bytes(viz_result["waveform"], f"{stem}_waveform.png", "image/png", FOLDER_VIZ),
            "melspec": upload_bytes(viz_result["melspec"], f"{stem}_melspec.png", "image/png", FOLDER_VIZ),
            "f0": upload_bytes(viz_result["f0"], f"{stem}_f0.png", "image/png", FOLDER_VIZ),
            "rms": upload_bytes(viz_result["rms"], f"{stem}_rms.png", "image/png", FOLDER_VIZ),
        }

        clip_id = insert_clip(
            labels=all_labels,
            uploader_name=uploader_name,
            original_filename=uploaded_file.name,
            stored_filename=stored_filename,
            drive_audio_file_id=audio_file_id,
            clip_length_sec=clip_length_sec,
            viz_file_ids=viz_file_ids,
        )

    st.success(f"업로드 완료! 저장된 파일명: {stored_filename} (clip_id={clip_id})")
    st.info("'클립 탐색' 페이지에서 시각화를 확인할 수 있습니다.")

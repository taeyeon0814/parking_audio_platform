# -*- coding: utf-8 -*-
"""클립 탐색: 오디오 미리듣기 + 음향 시각화 확인 (CLAUDE.md 4-1-C).

오디오/시각화는 Google Drive에서 서비스 계정 권한으로 내려받아 표시한다.
"""

import streamlit as st

from core.config import CONDITIONS, EXTRA_LABELS
from core.db import fetch_all_clips
from core.storage import download_bytes
from core.ui_common import require_auth_and_setup

st.set_page_config(page_title="클립 탐색", page_icon="🔊", layout="wide")

require_auth_and_setup()
st.title("🔊 클립 탐색")

clips = fetch_all_clips()
if not clips:
    st.info("아직 업로드된 클립이 없습니다. '업로드' 페이지에서 먼저 파일을 등록해주세요.")
    st.stop()

options = {f"[{c['clip_id']}] {c['stored_filename']}": c for c in clips}
selected_key = st.selectbox("클립 선택", list(options.keys()))
clip = options[selected_key]

st.subheader(clip["stored_filename"])

audio_file_id = clip.get("drive_audio_file_id")
if audio_file_id:
    try:
        with st.spinner("오디오 불러오는 중..."):
            audio_bytes = download_bytes(audio_file_id)
        st.audio(audio_bytes)
    except Exception as e:
        st.warning(f"오디오를 불러오지 못했습니다: {e}")
else:
    st.warning("오디오 파일 ID가 없습니다.")

st.markdown("### 라벨 정보")
label_cols = st.columns(5)
for col, (field, (label, _)) in zip(label_cols, CONDITIONS.items()):
    col.metric(label, clip.get(field) or "-")

extra_cols = st.columns(5)
for col, (field, (label, _)) in zip(extra_cols, EXTRA_LABELS.items()):
    col.metric(label, clip.get(field) or "-")

st.caption(
    f"업로더: {clip.get('uploader_name') or '-'} · "
    f"업로드 시각: {clip.get('uploaded_at') or '-'} · "
    f"클립 길이: {clip.get('clip_length_sec') and round(float(clip['clip_length_sec']), 2)}초"
)

st.divider()
st.markdown("### 음향 시각화")

viz_specs = [
    ("viz_waveform_file_id", "파형 (Waveform)"),
    ("viz_melspec_file_id", "멜 스펙트로그램 (Mel Spectrogram)"),
    ("viz_f0_file_id", "피치(F0) 궤적"),
    ("viz_rms_file_id", "RMS 에너지 (떨림/변동성 지표)"),
]

for field, title in viz_specs:
    file_id = clip.get(field)
    st.markdown(f"**{title}**")
    if file_id:
        try:
            img_bytes = download_bytes(file_id)
            st.image(img_bytes, use_container_width=True)
        except Exception as e:
            st.warning(f"이미지를 불러오지 못했습니다: {e}")
    else:
        st.warning("시각화 이미지가 없습니다. (업로드 시 생성 실패했을 수 있습니다)")

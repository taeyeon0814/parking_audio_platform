# -*- coding: utf-8 -*-
"""전체 데이터 조회: 라벨 필터링 + CSV 내보내기 (CLAUDE.md 4-1-E)."""

import pandas as pd
import streamlit as st

from core.config import CONDITIONS, EXTRA_LABELS
from core.db import fetch_all_clips
from core.ui_common import require_auth_and_setup

st.set_page_config(page_title="전체 데이터", page_icon="🗂️", layout="wide")

require_auth_and_setup()
st.title("🗂️ 전체 데이터 조회")

clips = fetch_all_clips()
if not clips:
    st.info("아직 업로드된 클립이 없습니다.")
    st.stop()

df = pd.DataFrame(clips)

st.subheader("라벨 필터")
filter_cols = st.columns(len(CONDITIONS))
active_filters = {}
for col, (field, (label, choices)) in zip(filter_cols, CONDITIONS.items()):
    selected = col.multiselect(label, choices, key=f"filter_{field}")
    if selected:
        active_filters[field] = selected

filtered_df = df.copy()
for field, selected in active_filters.items():
    filtered_df = filtered_df[filtered_df[field].isin(selected)]

st.caption(f"{len(filtered_df)}개 / 전체 {len(df)}개")

display_cols = (
    ["clip_id"]
    + list(CONDITIONS.keys())
    + list(EXTRA_LABELS.keys())
    + ["uploader_name", "original_filename", "stored_filename", "clip_length_sec", "uploaded_at"]
)
display_cols = [c for c in display_cols if c in filtered_df.columns]

rename_map = {f: label for f, (label, _) in CONDITIONS.items()}
rename_map.update({f: label for f, (label, _) in EXTRA_LABELS.items()})

st.dataframe(filtered_df[display_cols].rename(columns=rename_map), use_container_width=True, hide_index=True)

csv_bytes = filtered_df[display_cols].rename(columns=rename_map).to_csv(index=False).encode("utf-8-sig")
st.download_button("CSV로 내보내기", csv_bytes, file_name="clips_metadata.csv", mime="text/csv")

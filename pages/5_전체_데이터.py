# -*- coding: utf-8 -*-
"""전체 데이터 조회: 라벨 필터링 + CSV 내보내기 + 선택 삭제 (CLAUDE.md 4-1-E)."""

import pandas as pd
import streamlit as st

from core.config import CONDITIONS, EXTRA_LABELS
from core.db import fetch_all_clips
from core.clip_actions import delete_clips
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

st.divider()
st.subheader("선택 삭제")

select_all = st.checkbox("전체 선택", key="select_all_clips")

table_df = filtered_df[["clip_id"] + display_cols[1:]].copy()
table_df.insert(0, "선택", select_all)
table_df = table_df.rename(columns=rename_map)

edited_df = st.data_editor(
    table_df,
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in table_df.columns if c != "선택"],
    key="clips_data_editor",
)

selected_clip_ids = edited_df.loc[edited_df["선택"], "clip_id"].tolist()

confirm_key = "confirm_delete_bulk"

if selected_clip_ids:
    st.write(f"선택된 클립: {len(selected_clip_ids)}개")
    if not st.session_state.get(confirm_key):
        if st.button("🗑️ 선택 항목 삭제", type="primary"):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        st.warning(
            f"선택한 {len(selected_clip_ids)}개 클립을 삭제하면 되돌릴 수 없습니다. "
            "Drive의 오디오/시각화 파일과 Sheets의 기록이 모두 삭제됩니다."
        )
        c1, c2 = st.columns(2)
        if c1.button("네, 삭제합니다", type="primary", key="confirm_bulk_yes"):
            with st.spinner("삭제 중..."):
                deleted_count, errors = delete_clips(selected_clip_ids)
            st.session_state.pop(confirm_key, None)
            if deleted_count:
                st.success(f"{deleted_count}개 클립 삭제 완료.")
            if errors:
                st.warning("일부 Drive 파일 삭제에 실패했습니다: " + "; ".join(errors))
            st.rerun()
        if c2.button("취소", key="confirm_bulk_no"):
            st.session_state.pop(confirm_key, None)
            st.rerun()
else:
    st.session_state.pop(confirm_key, None)

st.divider()

csv_bytes = filtered_df[display_cols].rename(columns=rename_map).to_csv(index=False).encode("utf-8-sig")
st.download_button("CSV로 내보내기", csv_bytes, file_name="clips_metadata.csv", mime="text/csv")

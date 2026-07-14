# -*- coding: utf-8 -*-
"""수집 현황 대시보드 (CLAUDE.md 4-1-A)."""

import pandas as pd
import streamlit as st

from core.config import (
    CONDITIONS,
    condition_field_names,
    all_condition_combinations,
    TARGET_PER_CONDITION,
    total_target_clip_count,
)
from core.db import count_by_condition_combo
from core.ui_common import require_auth_and_setup

st.set_page_config(page_title="대시보드", page_icon="📊", layout="wide")

require_auth_and_setup()
st.title("📊 수집 현황 대시보드")

fields = condition_field_names()
combos = all_condition_combinations()
counts = count_by_condition_combo()

rows = []
for combo in combos:
    key = tuple(combo[f] for f in fields)
    cnt = counts.get(key, 0)
    row = {CONDITIONS[f][0]: combo[f] for f in fields}
    row["수집개수"] = cnt
    row["목표"] = TARGET_PER_CONDITION
    row["진행률(%)"] = round(min(cnt, TARGET_PER_CONDITION) / TARGET_PER_CONDITION * 100, 1)
    rows.append(row)

df = pd.DataFrame(rows)

total_collected = int(df["수집개수"].sum())
total_target = total_target_clip_count()

c1, c2, c3 = st.columns(3)
c1.metric("전체 수집 개수", f"{total_collected:,}개")
c2.metric("전체 목표 개수", f"{total_target:,}개")
c3.metric("전체 진행률", f"{min(total_collected, total_target) / total_target * 100:.1f}%")

st.progress(min(total_collected / total_target, 1.0))

st.divider()

st.subheader("조건 2축 히트맵")
axis_labels = {v[0]: k for k, v in CONDITIONS.items()}
label_names = list(axis_labels.keys())
colA, colB = st.columns(2)
x_label = colA.selectbox("X축", label_names, index=label_names.index("거리") if "거리" in label_names else 0)
y_label = colB.selectbox("Y축", label_names, index=label_names.index("방향") if "방향" in label_names else 1)
x_field = axis_labels[x_label]
y_field = axis_labels[y_label]

if x_field == y_field:
    st.warning("X축과 Y축은 서로 다른 항목을 선택해주세요.")
else:
    pivot = df.pivot_table(
        index=CONDITIONS[y_field][0],
        columns=CONDITIONS[x_field][0],
        values="수집개수",
        aggfunc="sum",
    )
    st.dataframe(
        pivot.style.background_gradient(cmap="RdYlGn", vmin=0, vmax=TARGET_PER_CONDITION),
        use_container_width=True,
    )

st.divider()

st.subheader("미채료 조건 목록 (부족한 순)")
short_df = df[df["수집개수"] < TARGET_PER_CONDITION].copy()
short_df["부족개수"] = TARGET_PER_CONDITION - short_df["수집개수"]
short_df = short_df.sort_values("부족개수", ascending=False)
st.dataframe(short_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("전체 조건 목록")
st.dataframe(df.sort_values("진행률(%)"), use_container_width=True, hide_index=True)

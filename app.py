# -*- coding: utf-8 -*-
"""Streamlit 엔트리 포인트. 공용 비밀번호 게이트 + 홈 화면.

페이지 이동은 왼쪽 사이드바(pages/ 자동 라우팅)를 사용.
"""

import streamlit as st

from core.db import init_db
from core.config import total_condition_count, total_target_clip_count

st.set_page_config(page_title="지하주차장 차량 경보음 데이터셋 플랫폼", page_icon="🅿️", layout="wide")

APP_PASSWORD = st.secrets.get("app_password", "parking2026")


def check_password() -> bool:
    if st.session_state.get("authed"):
        return True

    st.title("🅿️ 지하주차장 차량 경보음 데이터셋 플랫폼")
    st.caption("팀 공용 비밀번호를 입력하세요.")
    pw = st.text_input("비밀번호", type="password")
    if st.button("입장"):
        if pw == APP_PASSWORD:
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    return False


if not check_password():
    st.stop()

try:
    init_db()
except Exception as e:
    st.error(
        "Google Drive/Sheets 연동 설정이 아직 완료되지 않았습니다. "
        "SETUP.md를 참고해 서비스 계정과 secrets.toml을 설정해주세요.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()

st.title("🅿️ 지하주차장 차량 경보음 데이터셋 플랫폼")
st.markdown(
    """
    지하주차장 차량 경보음 기반 위치추정 오디오 데이터셋 구축 프로젝트의 팀 공용 플랫폼입니다.

    왼쪽 사이드바에서 원하는 페이지로 이동하세요.
    - **대시보드**: 96개 조건별 수집 현황
    - **업로드**: 오디오 클립 업로드 + 라벨링
    - **클립 탐색**: 업로드된 클립의 음향 시각화 확인
    - **자료실**: 발표자료/회의록/논문 등 문서 공유
    - **전체 데이터**: 라벨 필터링 + CSV 내보내기
    """
)

col1, col2 = st.columns(2)
col1.metric("총 조건 수", f"{total_condition_count()}개")
col2.metric("목표 클립 수", f"{total_target_clip_count()}개")

st.info("실험 설계 및 조건 정의는 프로젝트 루트의 CLAUDE.md를 참고하세요.")

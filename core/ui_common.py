# -*- coding: utf-8 -*-
"""페이지 공통 진입부 로직: 인증 확인 + Sheets/Drive 연동 초기화.

Google 연동 설정(secrets.toml)이 안 되어 있을 때 전체 스택트레이스 대신
친절한 안내 메시지를 보여주기 위해 각 페이지에서 이 함수를 사용한다.
"""

import streamlit as st

from core.db import init_db


def require_auth_and_setup():
    """비로그인/미설정 상태면 st.stop()으로 페이지 실행을 중단한다."""
    if not st.session_state.get("authed"):
        st.warning("메인 페이지에서 먼저 비밀번호를 입력해주세요.")
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

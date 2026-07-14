# -*- coding: utf-8 -*-
"""Google 인증. Drive/Sheets 클라이언트를 캐싱해서 제공한다.

서비스 계정은 자체 저장 용량(storage quota)이 0이라 개인 Drive에 새 파일을
업로드할 수 없다(Google 정책, storageQuotaExceeded). 그래서 서비스 계정이 아니라
OAuth로 실제 개인 Google 계정에 위임받아 인증한다 — 업로드된 파일은 그 개인 계정
소유가 되고, 계정의 Drive 용량을 그대로 사용한다.

자격증명은 Streamlit secrets(st.secrets["google_oauth"])의 client_id/client_secret/
refresh_token 3개로 구성한다. refresh_token은 scripts/get_refresh_token.py를 한 번
실행해서 발급받는다 (SETUP.md 참고).
"""

import streamlit as st
from google.oauth2.credentials import Credentials
import gspread
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

TOKEN_URI = "https://oauth2.googleapis.com/token"


def _load_credentials() -> Credentials:
    if "google_oauth" not in st.secrets:
        raise RuntimeError(
            "Google OAuth 자격증명을 찾을 수 없습니다. "
            ".streamlit/secrets.toml의 [google_oauth] 섹션(client_id/client_secret/"
            "refresh_token)을 채우세요. SETUP.md 참고."
        )
    cfg = st.secrets["google_oauth"]
    return Credentials(
        token=None,
        refresh_token=cfg["refresh_token"],
        token_uri=TOKEN_URI,
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        scopes=SCOPES,
    )


@st.cache_resource
def get_gspread_client():
    creds = _load_credentials()
    return gspread.authorize(creds)


@st.cache_resource
def get_drive_service():
    creds = _load_credentials()
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def drive_folder_id(folder_key: str) -> str:
    """secrets [drive_folders] 섹션에서 폴더 ID 조회. folder_key: audio/viz/docs"""
    return st.secrets["drive_folders"][folder_key]


def spreadsheet_id() -> str:
    return st.secrets["google_sheets"]["spreadsheet_id"]

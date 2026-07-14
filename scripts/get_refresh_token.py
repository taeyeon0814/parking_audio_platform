# -*- coding: utf-8 -*-
"""1회성 로컬 스크립트: 브라우저로 Google 로그인/동의를 받아 refresh_token을 발급받는다.

사전 준비 (GCP 콘솔, SETUP.md 참고):
1. API 및 서비스 → 사용자 인증 정보 → OAuth 클라이언트 ID 만들기 → 유형: "데스크톱 앱"
2. 생성된 client_id / client_secret을 아래 실행 시 --client-id, --client-secret으로 전달

실행:
    python scripts/get_refresh_token.py --client-id XXX --client-secret YYY

브라우저가 열리면 플랫폼에서 사용할 Google 계정으로 로그인하고 권한을 허용하세요.
완료되면 터미널에 [google_oauth] 섹션에 넣을 값이 출력됩니다.
"""

import argparse

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    args = parser.parse_args()

    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n=== 아래 내용을 .streamlit/secrets.toml의 [google_oauth] 섹션에 넣으세요 ===\n")
    print("[google_oauth]")
    print(f'client_id = "{creds.client_id}"')
    print(f'client_secret = "{creds.client_secret}"')
    print(f'refresh_token = "{creds.refresh_token}"')
    print()


if __name__ == "__main__":
    main()

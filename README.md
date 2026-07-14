# 지하주차장 차량 경보음 데이터셋 관리 플랫폼

실험 설계와 요구사항은 [CLAUDE.md](CLAUDE.md)를 참고하세요.

오디오 파일/시각화는 **Google Drive**, 메타데이터(라벨/클립 정보)는 **Google Sheets**에
저장됩니다. 처음 설정하는 경우 **[SETUP.md](SETUP.md)를 먼저 따라 하세요** (서비스 계정,
Drive 폴더, Sheets 생성 + Streamlit Cloud 배포 방법 포함).

## 실행 방법 (설정 완료 후)

```bash
cd parking_audio_platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # 값 채우기 (SETUP.md 참고)
streamlit run app.py
```

공용 비밀번호는 `.streamlit/secrets.toml`의 `app_password` 값으로 지정합니다 (기본값 `parking2026`).

## 배포

목표는 "내 컴퓨터를 꺼도 팀원 누구나 접속 가능한 공개 URL"입니다. 데이터가 전부 Google
Drive/Sheets에 있으므로 Streamlit Community Cloud처럼 재시작 시 로컬 파일이 초기화되는
호스팅에도 안전하게 배포할 수 있습니다. 자세한 절차는
[SETUP.md 5장](SETUP.md#5-streamlit-community-cloud-배포-외부-공개-url) 참고.

## 프로젝트 구조

```
parking_audio_platform/
├── CLAUDE.md
├── SETUP.md              # Google Drive/Sheets + Streamlit Cloud 설정 가이드
├── app.py                # Streamlit 엔트리 (비밀번호 게이트 + 홈)
├── pages/
│   ├── 1_대시보드.py       # 96조건 수집 현황
│   ├── 2_업로드.py         # 오디오 업로드 + 라벨링 (자동 리네임, Drive 업로드)
│   ├── 3_클립_탐색.py      # 파형/멜스펙트로그램/F0/RMS 시각화
│   ├── 4_자료실.py         # 팀 문서 공유 (Drive)
│   └── 5_전체_데이터.py     # 필터링 + CSV 내보내기
├── core/
│   ├── config.py          # 조건/라벨 정의 (single source of truth)
│   ├── gcp_auth.py         # Google 서비스 계정 인증 (Drive/Sheets 클라이언트)
│   ├── db.py               # Google Sheets 기반 메타데이터 저장소
│   ├── storage.py          # Google Drive 업로드/다운로드 (교체 가능하게 추상화)
│   ├── naming.py           # 파일명 규칙 생성
│   ├── audio_viz.py        # 음향 시각화 생성 (bytes 반환)
│   ├── cutting.py          # 원본 비상 오디오 자동 커팅 (2차 목표)
│   └── ui_common.py        # 페이지 공통 인증/초기화 헬퍼
├── .streamlit/
│   └── secrets.toml.example  # secrets.toml 템플릿 (실제 값은 gitignore)
└── requirements.txt
```

## 초기 버전 안내

이 플랫폼은 8/18 데이터 수집 시작 전 MVP 수준으로 구축되었습니다. 앞으로 다음이 조금씩
추가/수정될 예정입니다 (CLAUDE.md 5장 우선순위 참고):

- 일괄 업로드 + CSV 라벨 매칭
- 긴 원본 비상 업로드 시 서버 자동 커팅 통합
- jitter/shimmer 등 고급 음향 지표
- Google Sheets 행 수가 커질 경우 캐싱/페이지네이션 최적화

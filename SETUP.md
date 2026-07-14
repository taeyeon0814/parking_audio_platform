# 설정 가이드: Google Drive/Sheets 연동 + Streamlit Cloud 배포

이 플랫폼은 오디오 파일과 시각화 이미지를 **Google Drive**에, 메타데이터(라벨/클립 정보)를
**Google Sheets**에 저장합니다.

> ⚠️ **서비스 계정이 아니라 OAuth(개인 Google 계정 위임)를 사용합니다.** 서비스 계정은
> 자체 Drive 저장 용량이 0이라(`storageQuotaExceeded`) 개인 Drive에 새 파일을 올릴 수
> 없습니다 (Google Workspace 공유 드라이브가 있으면 서비스 계정도 가능하지만, 일반
> Gmail 계정에는 없는 기능입니다). 그래서 앱이 실제 개인 Google 계정에 위임받아
> 그 계정의 Drive 용량으로 파일을 저장하도록 구성합니다.

아래 순서대로 한 번만 설정하면 됩니다. (팀 계정 소유자 1명이 진행)

---

## 1. Google Cloud 프로젝트 생성 + API 활성화

1. https://console.cloud.google.com 접속 → 새 프로젝트 생성 (예: `parking-audio-platform`)
2. 좌측 메뉴 **API 및 서비스 → 라이브러리**에서 아래 2개 API를 각각 검색해 **사용 설정**
   - Google Drive API
   - Google Sheets API

---

## 2. OAuth 동의 화면 설정

1. **API 및 서비스 → OAuth 동의 화면**으로 이동
2. User Type: **외부(External)** 선택 → 앱 이름/이메일 등 기본 정보 입력
3. 범위(Scopes) 추가: `.../auth/drive`, `.../auth/spreadsheets`
4. **게시 상태(Publishing status)를 "테스트(Testing)"가 아니라 "프로덕션(In production)"으로
   전환하세요.** (중요) "테스트" 상태로 두면 발급되는 refresh_token이 7일 후 만료되어
   서버가 조용히 인증 실패하게 됩니다. "프로덕션"으로 전환하면(구글 심사 없이도 전환 가능,
   단 로그인 시 "확인되지 않은 앱" 경고가 뜸) refresh_token이 만료되지 않습니다.

---

## 3. OAuth 클라이언트 ID 생성

1. **API 및 서비스 → 사용자 인증 정보 → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID**
2. 애플리케이션 유형: **데스크톱 앱**
3. 생성된 **클라이언트 ID**와 **클라이언트 보안 비밀**을 복사해둡니다.

---

## 4. Google Drive 폴더 3개 생성

플랫폼에서 쓸 개인(또는 팀 공용) Google Drive에 폴더 3개를 만듭니다.

- `parking_audio/audio` — 오디오 원본
- `parking_audio/viz` — 시각화 PNG 캐시
- `parking_audio/docs` — 자료실 문서

각 폴더의 URL에서 폴더 ID를 복사해둡니다.
`https://drive.google.com/drive/folders/`**`이 부분이 폴더 ID`**

(서비스 계정 방식과 달리 별도 공유 설정은 필요 없습니다 — 이 계정이 폴더 소유자입니다.)

---

## 5. Google Sheets 생성

새 Google Sheets 문서를 하나 만듭니다 (예: `parking_audio_metadata`). 시트/헤더 행은
앱이 처음 접속할 때 자동으로 생성하므로 미리 만들 필요 없습니다.

URL에서 스프레드시트 ID를 복사해둡니다.
`https://docs.google.com/spreadsheets/d/`**`이 부분이 스프레드시트 ID`**`/edit`

---

## 6. refresh_token 발급 (1회성, 로컬에서 실행)

```bash
cd parking_audio_platform
source .venv/bin/activate
pip install -r requirements.txt
python scripts/get_refresh_token.py --client-id "3단계에서_복사한_클라이언트ID" --client-secret "3단계에서_복사한_클라이언트보안비밀"
```

브라우저가 자동으로 열립니다. 플랫폼에서 사용할 Google 계정으로 로그인하고 권한을
허용하세요 ("확인되지 않은 앱" 경고가 뜨면 **고급 → OOO(으)로 이동(안전하지 않음)** 클릭).
완료되면 터미널에 `[google_oauth]` 섹션 값이 출력됩니다.

---

## 7. secrets.toml 작성

`.streamlit/secrets.toml.example`을 복사해 `.streamlit/secrets.toml`로 저장하고 값을 채웁니다.

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

- `[google_oauth]`: 6단계에서 출력된 client_id / client_secret / refresh_token
- `[drive_folders]`: 4단계에서 복사한 폴더 ID 3개
- `[google_sheets].spreadsheet_id`: 5단계에서 복사한 스프레드시트 ID (URL 전체가 아니라 ID만!)
- `app_password`: 팀 공용 접속 비밀번호 (원하는 값으로 변경)

이 파일은 `.gitignore`에 포함되어 있어 git에 올라가지 않습니다.

### 로컬 실행 확인

```bash
streamlit run app.py
```

비밀번호 입력 후 정상적으로 대시보드가 뜨면 설정 완료입니다. 업로드 페이지에서 테스트
파일을 하나 올려 Drive 폴더/Sheets에 실제로 기록되는지 확인해보세요.

---

## 8. Streamlit Community Cloud 배포 (외부 공개 URL)

> ✅ 오디오/이미지를 Google Drive에, 메타데이터를 Google Sheets에 저장하므로 컨테이너가
> 재시작돼도 데이터가 사라지지 않습니다 — 내 컴퓨터를 꺼도 팀원 누구나 접속 가능한 공개
> URL로 배포할 수 있습니다.

1. 이 프로젝트를 GitHub 저장소에 push (단, `.streamlit/secrets.toml`은 `.gitignore`로
   제외되어 있어 자동으로 올라가지 않습니다 — 확인하세요)
2. https://share.streamlit.io 접속 → GitHub 계정 연동 → **New app**
3. 저장소/브랜치 선택, **Main file path**: `app.py`
4. **Advanced settings → Secrets**에 `.streamlit/secrets.toml`에 채운 내용을 그대로 붙여넣기
5. **Deploy** 클릭 → 빌드가 끝나면 `https://<app-name>.streamlit.app` 형태의 공개 URL 발급

이 URL을 팀원들에게 공유하면 됩니다. 내 컴퓨터를 꺼도 URL은 계속 살아있고, 데이터도
Drive/Sheets에 있으므로 그대로 유지됩니다.

### 배포 후 코드/설정을 바꿀 때
- 코드: GitHub에 push하면 Streamlit Cloud가 자동으로 재배포합니다.
- 폴더/시트 ID, 비밀번호 등: Streamlit Cloud 앱 설정의 **Secrets**를 수정하고 앱을 Reboot 하세요.

---

## 트러블슈팅

- **"Google OAuth 자격증명을 찾을 수 없습니다"**: secrets.toml이 없거나 `[google_oauth]`
  섹션이 비어있습니다. 7단계를 다시 확인하세요.
- **`storageQuotaExceeded`**: 서비스 계정 방식으로 되돌아간 것입니다. `core/gcp_auth.py`가
  `google.oauth2.credentials.Credentials`(OAuth)를 쓰고 있는지, secrets에 `[google_oauth]`가
  있는지 확인하세요.
- **refresh_token이 며칠 뒤 갑자기 안 됨**: OAuth 동의 화면 게시 상태가 "테스트"로 되어
  있을 가능성이 큽니다. 2단계에서 "프로덕션"으로 전환하고 6단계를 다시 실행해 새
  refresh_token을 발급받으세요.
- **API has not been used / disabled**: 1단계에서 Drive API, Sheets API 둘 다
  사용 설정했는지 확인하세요.

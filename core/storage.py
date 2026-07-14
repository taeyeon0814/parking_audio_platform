# -*- coding: utf-8 -*-
"""파일 저장/조회. Google Drive를 백엔드로 사용 (CLAUDE.md 4-2/4-3 설계 결정 반영).

CLAUDE.md 4-3에서 언급한 "저장 백엔드만 storage.py 교체" 원칙에 따라, 이 모듈만
바꾸면 로컬 디스크 대신 Drive를 쓰도록 전환할 수 있다. 오디오/시각화/문서 3종
폴더는 Streamlit secrets의 [drive_folders]에 폴더 ID로 지정한다.

파일은 서비스 계정 소유로 업로드되며, 공개 링크를 만들지 않는다(비공개 유지).
재생/표시가 필요할 때마다 서버(서비스 계정 권한)로 바이트를 내려받아 스트림릿에 전달한다.
"""

import io

from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from core.gcp_auth import get_drive_service, drive_folder_id

FOLDER_AUDIO = "audio"
FOLDER_VIZ = "viz"
FOLDER_DOCS = "docs"


def upload_bytes(data: bytes, filename: str, mime_type: str, folder_key: str) -> str:
    """bytes를 지정한 Drive 폴더에 업로드하고 file_id를 반환한다."""
    service = get_drive_service()
    metadata = {"name": filename, "parents": [drive_folder_id(folder_key)]}
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime_type, resumable=False)
    file = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return file["id"]


def download_bytes(file_id: str) -> bytes:
    """Drive file_id의 내용을 bytes로 내려받는다."""
    if not file_id:
        raise ValueError("file_id가 비어 있습니다.")
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def delete_file(file_id: str):
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()

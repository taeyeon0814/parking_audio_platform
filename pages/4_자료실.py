# -*- coding: utf-8 -*-
"""자료실: 발표자료/회의록/논문 등 문서 업로드/다운로드 (CLAUDE.md 4-1-D).

문서 파일은 Google Drive docs 폴더에 저장하고, 메타데이터는 Google Sheets에 기록한다.
"""

import mimetypes

import streamlit as st

from core.db import insert_document, fetch_all_documents
from core.storage import upload_bytes, download_bytes, FOLDER_DOCS
from core.ui_common import require_auth_and_setup

st.set_page_config(page_title="자료실", page_icon="📁", layout="wide")

require_auth_and_setup()

st.title("📁 자료실")
st.caption("발표자료(PPT/PDF), 회의록, 참고 논문 등 팀 문서를 Google Drive에 공유합니다.")

with st.form("doc_upload_form", clear_on_submit=True):
    title = st.text_input("문서 제목")
    uploader_name = st.text_input("업로더 이름")
    doc_file = st.file_uploader("문서 파일", type=["pdf", "ppt", "pptx", "doc", "docx", "hwp", "txt", "md", "zip"])
    submitted = st.form_submit_button("업로드", type="primary")

    if submitted:
        if not title.strip() or not uploader_name.strip() or doc_file is None:
            st.error("제목, 업로더 이름, 파일을 모두 입력해주세요.")
        else:
            with st.spinner("Google Drive 업로드 중..."):
                mime_type = mimetypes.guess_type(doc_file.name)[0] or "application/octet-stream"
                file_id = upload_bytes(doc_file.getvalue(), doc_file.name, mime_type, FOLDER_DOCS)
                insert_document(title, doc_file.name, file_id, uploader_name)
            st.success(f"'{title}' 업로드 완료.")
            st.rerun()

st.divider()
st.subheader("문서 목록")

docs = fetch_all_documents()
if not docs:
    st.info("등록된 문서가 없습니다.")
else:
    for d in docs:
        col1, col2, col3 = st.columns([3, 2, 2])
        col1.markdown(f"**{d['title']}**  \n`{d['original_filename']}`")
        col2.caption(f"업로더: {d['uploader_name'] or '-'}  \n{d['uploaded_at']}")
        file_id = d.get("drive_file_id")
        if file_id:
            if col3.button("다운로드 준비", key=f"prep_{d['doc_id']}"):
                with st.spinner("불러오는 중..."):
                    data = download_bytes(file_id)
                st.download_button(
                    "다운로드",
                    data,
                    file_name=d["original_filename"],
                    key=f"dl_{d['doc_id']}",
                )
        else:
            col3.warning("파일 없음")

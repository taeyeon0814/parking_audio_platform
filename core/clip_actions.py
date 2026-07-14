# -*- coding: utf-8 -*-
"""클립 삭제 등 여러 페이지에서 공용으로 쓰는 동작 모음.

삭제는 Sheets 행 제거 + Drive 파일(오디오/시각화 4종) 제거를 함께 수행한다.
개별 파일 삭제가 실패해도(이미 지워졌거나 권한 문제) 전체 작업이 중단되지 않도록
파일 단위로 오류를 흡수하고, 실패 목록을 반환한다.
"""

from core.db import delete_clips as _delete_clips_from_sheet
from core.storage import delete_file


def delete_clips(clip_ids):
    """clip_id 목록을 Sheets + Drive에서 모두 삭제한다.

    반환: (성공한 clip_id 개수, 실패한 Drive 파일 삭제 오류 메시지 목록)
    """
    file_ids_by_clip = _delete_clips_from_sheet(clip_ids)

    drive_errors = []
    for clip_id, file_ids in file_ids_by_clip.items():
        for file_id in file_ids:
            if not file_id:
                continue
            try:
                delete_file(file_id)
            except Exception as e:
                drive_errors.append(f"clip_id={clip_id} file_id={file_id}: {e}")

    return len(file_ids_by_clip), drive_errors

"""CSV 파일을 읽어 열 이름과 행 목록으로 돌려주는 CSVDataLoader 클래스.

담당: 김현수
"""
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Union

Source = Union[str, Path, bytes]


class CSVDataLoader:
    # 서울시 CSV는 대부분 CP949(엑셀 한글)라서 여러 인코딩을 차례로 시도한다.
    ENCODINGS = ("utf-8-sig", "cp949", "euc-kr")

    def __init__(self, source: Source) -> None:
        self._source = source
        self.encoding: str = ""

    def read(self) -> tuple[list[str], list[dict]]:
        """(열 이름 목록, 행 dict 목록)을 반환한다."""
        text = self._decode(self._read_bytes())
        reader = csv.DictReader(io.StringIO(text))
        headers = [h.strip() for h in (reader.fieldnames or [])]
        reader.fieldnames = headers
        return headers, list(reader)

    def _read_bytes(self) -> bytes:
        if isinstance(self._source, bytes):
            return self._source
        return Path(self._source).read_bytes()

    def _decode(self, raw: bytes) -> str:
        for encoding in self.ENCODINGS:
            try:
                text = raw.decode(encoding)
                self.encoding = encoding
                return text
            except UnicodeDecodeError:
                continue
        # 서울시 원본 CSV에는 깨진 글자가 몇 개 섞여 있어 엄격하게 읽으면 실패한다.
        # 그 글자만 �로 바꾸고 나머지는 그대로 읽는다.
        self.encoding = "cp949 (깨진 글자 대체)"
        return raw.decode("cp949", errors="replace")

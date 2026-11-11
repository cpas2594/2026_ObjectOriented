"""CSV 한 행을 정리하는 DataCleaner 클래스.

담당: 김현수

- 실제 열 이름을 내부 필드 이름(company, title, ...)으로 맞춘다.
- 공백·결측치를 정리하고, 주소에서 서울 자치구를 찾는다.
"""
from __future__ import annotations

from typing import Optional

from ..config import SEOUL_DISTRICTS
from ..models import JobPosting
from .columns import COLUMN_ALIASES, LOCATION_COLUMNS, REQUIRED_COLUMNS


class DataCleaner:
    def __init__(self, headers: list[str]) -> None:
        self._column_map = self.build_column_map(headers)

    @property
    def column_map(self) -> dict[str, str]:
        return dict(self._column_map)

    @staticmethod
    def build_column_map(headers: list[str]) -> dict[str, str]:
        """{내부 필드명: 실제 CSV 열 이름} 매핑을 만든다. 필수 열이 없으면 ValueError."""
        header_set = set(headers)
        column_map = {}
        for field, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in header_set:
                    column_map[field] = alias
                    break

        missing = [f for f in REQUIRED_COLUMNS if f not in column_map]
        if not any(f in column_map for f in LOCATION_COLUMNS):
            missing.append(" 또는 ".join(LOCATION_COLUMNS))
        if missing:
            raise ValueError(
                f"필수 열을 찾지 못했습니다: {missing}. CSV 열 이름: {headers}. "
                "jobdash/data_processing/columns.py의 COLUMN_ALIASES에 열 이름을 추가해 주세요."
            )
        return column_map

    def clean_row(self, raw: dict) -> Optional[dict]:
        """CSV 한 행을 내부 필드명 기준 dict로 정리한다. 회사명/제목이 없으면 None."""
        row = {
            field: JobPosting.normalize_text(raw.get(column, ""))
            for field, column in self._column_map.items()
        }
        if not row.get("company") or not row.get("title"):
            return None

        district = row.get("district", "")
        if district not in SEOUL_DISTRICTS:
            district = self.extract_district(row.get("address", "") or district)
        row["district"] = district
        return row

    @staticmethod
    def extract_district(address: str) -> str:
        """주소 문자열에서 서울 자치구 이름을 찾는다. 서울이 아니면 빈 문자열."""
        if not address:
            return ""
        if "서울" not in address and not any(address.startswith(d) for d in SEOUL_DISTRICTS):
            return ""
        for token in address.replace(",", " ").split():
            if token in SEOUL_DISTRICTS:
                return token
        # 띄어쓰기가 없는 주소 대비: 긴 이름부터 비교
        for name in sorted(SEOUL_DISTRICTS, key=len, reverse=True):
            if name in address:
                return name
        return ""

"""JobPosting 객체 목록을 보관하고 필터링·검색하는 JobDataManager 클래스.

담당: 김현수 (로딩), 한예승 (검색)

적용 개념
- Composition: 읽기는 CSVDataLoader, 정리는 DataCleaner 객체에 맡긴다.
- Collection Framework: 공고 객체는 list, 자치구 묶음은 dict, 중복 확인·고유값은 set
- Single Responsibility: 데이터 보관·조회만 하고 통계 계산은 Analyzer에 맡긴다.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Optional

from ..config import SEOUL_DISTRICTS
from ..models import JobPosting
from .csv_loader import CSVDataLoader, Source
from .data_cleaner import DataCleaner


class JobDataManager:
    SEOUL_DISTRICTS = SEOUL_DISTRICTS

    def __init__(self, jobs: Optional[Iterable[JobPosting]] = None) -> None:
        self._jobs: list[JobPosting] = list(jobs or [])
        self.load_report: dict = {}

    # ── 생성/로딩 ─────────────────────────────────────────────────────
    @classmethod
    def from_csv(cls, source: Source) -> "JobDataManager":
        manager = cls()
        manager.load(source)
        return manager

    def load(self, source: Source) -> int:
        """CSV를 읽고 정리해 JobPosting 객체 list로 저장한다. 저장된 개수를 반환."""
        headers, rows = CSVDataLoader(source).read()
        cleaner = DataCleaner(headers)

        jobs: list[JobPosting] = []
        seen: set[tuple] = set()  # 중복 공고 확인용
        report = {"원본 행": 0, "서울 외 지역": 0, "필수값 누락": 0, "중복": 0}

        for raw in rows:
            report["원본 행"] += 1
            cleaned = cleaner.clean_row(raw)
            if cleaned is None:
                report["필수값 누락"] += 1
                continue
            if not cleaned["district"]:
                report["서울 외 지역"] += 1
                continue

            job = JobPosting.from_row(cleaned)
            if not job.is_valid():
                report["필수값 누락"] += 1
                continue

            key = job.duplicate_key()
            if key in seen:
                report["중복"] += 1
                continue
            seen.add(key)
            jobs.append(job)

        report["사용한 공고"] = len(jobs)
        self._jobs = jobs
        self.load_report = report
        return len(jobs)

    # ── 조회 ──────────────────────────────────────────────────────────
    @property
    def jobs(self) -> tuple[JobPosting, ...]:
        """외부에서 내부 list를 직접 수정하지 못하게 tuple로 돌려준다."""
        return tuple(self._jobs)

    def __len__(self) -> int:
        return len(self._jobs)

    def filter_jobs(
        self,
        job_type: Optional[str] = None,
        career: Optional[str] = None,
        employment: Optional[str] = None,
        district: Optional[str] = None,
        job_group: Optional[str] = None,
        jobs: Optional[Iterable[JobPosting]] = None,
    ) -> list[JobPosting]:
        source = self._jobs if jobs is None else jobs
        return [
            job for job in source
            if job.matches_filter(job_type, career, employment, district, job_group)
        ]

    def search_jobs(self, keyword: str = "", **filters) -> list[JobPosting]:
        """검색어 + 필터를 함께 적용한다. 마감일이 가까운 순으로 정렬."""
        result = [job for job in self.filter_jobs(**filters) if job.matches_keyword(keyword)]
        return sorted(result, key=lambda j: (j.deadline == "", j.deadline))

    def unique_values(self, attribute: str, jobs: Optional[Iterable[JobPosting]] = None) -> list[str]:
        """특정 속성의 고유값 목록 (필터 선택지용)."""
        values = {getattr(job, attribute) for job in (self._jobs if jobs is None else jobs)}
        values.discard("")
        return sorted(values)

    def group_by_district(self, jobs: Optional[Iterable[JobPosting]] = None) -> dict[str, list[JobPosting]]:
        groups: dict[str, list[JobPosting]] = defaultdict(list)
        for job in (self._jobs if jobs is None else jobs):
            groups[job.get_district()].append(job)
        return dict(groups)

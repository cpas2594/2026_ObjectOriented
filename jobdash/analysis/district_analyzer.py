"""자치구별 집계와 분포 통계를 계산하는 DistrictAnalyzer.

담당: 박수연

적용 개념: Inheritance(JobAnalyzer 상속), Polymorphism(analyze() 재정의)
"""
from __future__ import annotations

from typing import Iterable

from ..models import JobPosting
from .base import JobAnalyzer


class DistrictAnalyzer(JobAnalyzer):
    def __init__(self, jobs: Iterable[JobPosting], districts: Iterable[str] = ()) -> None:
        super().__init__(jobs)
        # 공고가 0건인 구도 지도에 나오도록 전체 자치구 목록을 받는다.
        self._districts = tuple(districts)

    def analyze(self) -> dict:
        by_district = {d: {"공고 수": 0, "모집인원": 0} for d in self._districts}
        for job in self._jobs:
            stats = by_district.setdefault(job.get_district(), {"공고 수": 0, "모집인원": 0})
            stats["공고 수"] += 1
            stats["모집인원"] += job.headcount

        return {
            "summary": self.summarize(),
            "by_district": by_district,
            "distributions": {
                "직종 분류": self.count_by(lambda j: j.job_group, top=10),
                "직종": self.count_by(lambda j: j.job_type, top=10),
                "경력": self.count_by(lambda j: j.career_category),
                "고용형태": self.count_by(lambda j: j.employment_category),
                "학력": self.count_by(lambda j: j.education, top=8),
            },
        }

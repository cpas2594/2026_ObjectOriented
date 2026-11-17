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
        grouped: dict[str, list[JobPosting]] = {d: [] for d in self._districts}
        for job in self._jobs:
            grouped.setdefault(job.get_district(), []).append(job)
        by_district = {d: self._district_stats(jobs) for d, jobs in grouped.items()}

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

    def _district_stats(self, jobs: list[JobPosting]) -> dict:
        """한 자치구의 지도 기준 값들. 공고가 없으면 비율·평균은 0."""
        count = len(jobs)
        headcount = sum(j.headcount for j in jobs)
        return {
            "공고 수": count,
            "모집인원": headcount,
            "공고당 평균 모집인원": round(headcount / count, 1) if count else 0.0,
            "신입 가능 비율(%)": self.ratio_of(lambda j: j.is_entry_level(), jobs),
            "정규직 비율(%)": self.ratio_of(lambda j: j.is_regular(), jobs),
            "대졸 이상 요구 비율(%)": self.ratio_of(lambda j: j.is_college_or_above(), jobs),
        }

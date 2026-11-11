"""두 지역의 채용 특성 비율을 비교하는 ComparisonAnalyzer.

담당: 유해린

적용 개념: Inheritance(JobAnalyzer 상속), Polymorphism(analyze() 재정의)
비교 지표를 바꾸려면 METRICS에 (이름, 판정 메서드)를 추가·수정하면 된다.
"""
from __future__ import annotations

from typing import Callable, Iterable

from ..models import JobPosting
from .base import JobAnalyzer


class ComparisonAnalyzer(JobAnalyzer):
    METRICS: tuple[tuple[str, Callable[[JobPosting], bool]], ...] = (
        ("신입 가능률", JobPosting.is_entry_level),
        ("정규직률", JobPosting.is_regular),
        ("대졸 이상률", JobPosting.is_college_or_above),
        ("IT 직종률", JobPosting.is_it_job),
    )

    def __init__(
        self,
        base_jobs: Iterable[JobPosting],
        target_jobs: Iterable[JobPosting],
        base_label: str = "기준",
        target_label: str = "비교 대상",
    ) -> None:
        super().__init__(base_jobs)
        self._target_jobs = list(target_jobs)
        self._base_label = base_label
        self._target_label = target_label

    def analyze(self) -> dict:
        rows = []
        for name, predicate in self.METRICS:
            base = self.ratio_of(predicate)
            target = self.ratio_of(predicate, self._target_jobs)
            rows.append({
                "지표": name,
                self._base_label: base,
                self._target_label: target,
                "차이(%p)": round(base - target, 1),
            })
        return {
            "labels": (self._base_label, self._target_label),
            "counts": (len(self._jobs), len(self._target_jobs)),
            "metrics": rows,
        }

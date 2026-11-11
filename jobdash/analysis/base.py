"""모든 분석기의 부모 클래스 JobAnalyzer.

적용 개념
- Abstraction: analyze()는 추상 메서드라 자식 클래스가 반드시 구현한다.
- Refactoring: 비율·빈도 계산처럼 여러 분석기에서 반복되는 코드를 여기로 모았다.
- Open/Closed: 새 분석이 필요하면 이 클래스를 상속한 파일만 추가하면 된다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import Callable, Iterable, Optional

from ..models import JobPosting


class JobAnalyzer(ABC):
    def __init__(self, jobs: Iterable[JobPosting]) -> None:
        self._jobs: list[JobPosting] = list(jobs)

    @abstractmethod
    def analyze(self) -> dict:
        """자식 클래스가 목적에 맞게 재정의한다."""

    @staticmethod
    def calculate_ratio(part: int, whole: int) -> float:
        """백분율(소수 첫째 자리). 분모가 0이면 0.0."""
        return round(part / whole * 100, 1) if whole else 0.0

    def ratio_of(self, predicate: Callable[[JobPosting], bool], jobs=None) -> float:
        jobs = self._jobs if jobs is None else jobs
        return self.calculate_ratio(sum(1 for j in jobs if predicate(j)), len(jobs))

    def count_by(self, key: Callable[[JobPosting], str], jobs=None, top: Optional[int] = None) -> dict[str, int]:
        jobs = self._jobs if jobs is None else jobs
        return dict(Counter(key(j) for j in jobs).most_common(top))

    def summarize(self, jobs=None) -> dict:
        jobs = self._jobs if jobs is None else jobs
        return {
            "공고 수": len(jobs),
            "모집인원": sum(j.headcount for j in jobs),
            "신입 가능": sum(1 for j in jobs if j.is_entry_level()),
        }

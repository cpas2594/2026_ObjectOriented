"""통계 계산. 모든 분석기는 JobAnalyzer를 상속하고 analyze()를 구현한다."""
from .base import JobAnalyzer
from .comparison_analyzer import ComparisonAnalyzer
from .district_analyzer import DistrictAnalyzer

__all__ = ["JobAnalyzer", "DistrictAnalyzer", "ComparisonAnalyzer"]

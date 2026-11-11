"""화면(탭)별 그리기 함수. 각 모듈은 render() 하나를 제공한다."""
from . import comparison, district_detail, overview, search

__all__ = ["overview", "district_detail", "comparison", "search"]

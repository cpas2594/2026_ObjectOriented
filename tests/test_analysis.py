"""analysis/ : JobAnalyzer, DistrictAnalyzer, ComparisonAnalyzer 테스트."""
import pytest

from jobdash import ComparisonAnalyzer, DistrictAnalyzer, JobAnalyzer


def test_abstract_parent():
    with pytest.raises(TypeError):
        JobAnalyzer([])
    assert JobAnalyzer.calculate_ratio(1, 0) == 0.0
    assert JobAnalyzer.calculate_ratio(1, 3) == 33.3


def test_district_analyzer(make_job):
    jobs = [make_job(), make_job(district="마포구", career="경력")]
    result = DistrictAnalyzer(jobs, ["강남구", "마포구", "중구"]).analyze()
    assert result["by_district"]["중구"]["공고 수"] == 0
    assert result["summary"] == {"공고 수": 2, "모집인원": 4, "신입 가능": 1}
    assert result["distributions"]["경력"] == {"신입": 1, "경력": 1}


def test_district_map_metrics(make_job):
    jobs = [make_job(), make_job(career="경력")]
    by_district = DistrictAnalyzer(jobs, ["강남구", "중구"]).analyze()["by_district"]
    gangnam, junggu = by_district["강남구"], by_district["중구"]
    assert gangnam["공고당 평균 모집인원"] == gangnam["모집인원"] / 2
    assert gangnam["신입 가능 비율(%)"] == 50.0
    assert junggu["공고당 평균 모집인원"] == 0.0 and junggu["정규직 비율(%)"] == 0.0


def test_comparison_analyzer(make_job):
    jobs = [make_job(), make_job(district="마포구", career="경력", job_code="026501")]
    result = ComparisonAnalyzer(jobs[:1], jobs, "강남구", "서울 전체").analyze()
    entry, _, _, it = result["metrics"]
    assert entry["강남구"] == 100.0 and entry["서울 전체"] == 50.0
    assert it["차이(%p)"] == 50.0


def test_polymorphism(make_job):
    """같은 analyze() 호출이 객체 종류에 따라 다른 결과를 낸다."""
    jobs = [make_job()]
    analyzers = [DistrictAnalyzer(jobs), ComparisonAnalyzer(jobs, jobs)]
    results = [a.analyze() for a in analyzers]
    assert "by_district" in results[0] and "metrics" in results[1]

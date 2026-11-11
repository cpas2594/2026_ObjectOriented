"""data_processing/ : CSVDataLoader, DataCleaner, JobDataManager 테스트."""
import pytest

from jobdash import CSVDataLoader, DataCleaner, JobDataManager

CSV_TEXT = (
    "기업명,채용제목,근무지역,경력,직종코드\n"
    "A사,개발,서울 강남구,신입,133200\n"
    "A사,개발,서울 강남구,신입,133200\n"      # 중복
    ",회계,서울 마포구,경력,026501\n"          # 회사명 누락
    "C사,영업,경기 수원시,관계없음,615400\n"    # 서울 외
    "D사,요양,서울 마포구,관계없음,550102\n"
)


def test_loader_reads_cp949_and_broken_bytes():
    raw = CSV_TEXT.encode("cp949") + b"E\x82,x,\xbc\xad\xbf\xef \xc1\xdf\xb1\xb8,y,1\n"
    loader = CSVDataLoader(raw)
    headers, rows = loader.read()
    assert headers[0] == "기업명" and len(rows) == 6
    assert "대체" in loader.encoding


@pytest.mark.parametrize("address, expected", [
    ("서울특별시 강남구 테헤란로 1", "강남구"),
    ("서울 중랑구", "중랑구"),
    ("서울특별시중구세종대로110", "중구"),
    ("경기 성남시 분당구", ""),
])
def test_extract_district(address, expected):
    assert DataCleaner.extract_district(address) == expected


def test_cleaner_missing_columns():
    with pytest.raises(ValueError):
        DataCleaner(["가", "나"])


def test_manager_load_report():
    manager = JobDataManager.from_csv(CSV_TEXT.encode("cp949"))
    assert len(manager) == 2
    assert manager.load_report == {
        "원본 행": 5, "서울 외 지역": 1, "필수값 누락": 1, "중복": 1, "사용한 공고": 2,
    }


def test_filter_search_and_group():
    manager = JobDataManager.from_csv(CSV_TEXT.encode("utf-8"))
    assert [j.company for j in manager.filter_jobs(district="마포구")] == ["D사"]
    assert len(manager.search_jobs("요양")) == 1
    assert set(manager.group_by_district()) == {"강남구", "마포구"}
    assert manager.unique_values("job_group") == ["돌봄 서비스직(간병·육아)", "정보통신 연구개발·공학기술직"]


def test_jobs_is_read_only_tuple():
    manager = JobDataManager.from_csv(CSV_TEXT.encode("utf-8"))
    assert isinstance(manager.jobs, tuple)

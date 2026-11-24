"""JobSearch / MainDashboard 중 화면과 무관한 부분 테스트."""
import pytest

pytest.importorskip("streamlit")  # streamlit이 없는 환경에서는 건너뜀

from jobdash import JobDataManager  # noqa: E402
from jobdash.config import ALL, SEOUL_DISTRICTS  # noqa: E402
from jobdash.ui.dashboard import MainDashboard  # noqa: E402
from jobdash.ui.views.search import JobSearch  # noqa: E402


@pytest.fixture
def searcher(make_job):
    jobs = [
        make_job(company="가나소프트", title="백엔드 개발자", district="강남구", deadline="2099-12-31"),
        make_job(company="다라회계", title="회계 사무원", job_type="회계 사무원", job_code="",
                 district="마포구", deadline="2099-12-31"),
        make_job(company="마바물류", title="물류 관리", district="강남구", deadline="2000-01-01"),
    ]
    return JobSearch(JobDataManager(jobs), list(SEOUL_DISTRICTS))


def test_search_by_keyword(searcher):
    results = searcher.search("회계", ALL, {"hide_expired": False})
    assert [job.company for job in results] == ["다라회계"]


def test_search_by_area(searcher):
    results = searcher.search("", "강남구", {"hide_expired": False})
    assert {job.company for job in results} == {"가나소프트", "마바물류"}


def test_search_hides_expired_when_filter_on(searcher):
    results = searcher.search("", "강남구", {"hide_expired": True})
    assert [job.company for job in results] == ["가나소프트"]


def test_summary_text_counts_expired(searcher):
    results = searcher.search("", ALL, {"hide_expired": False})
    assert searcher.summary_text(results) == "검색 결과 **3건** (마감 1건 포함)"
    assert searcher.summary_text([]) == "검색 결과 **0건**"


def test_to_table_has_one_row_per_job(searcher):
    results = searcher.search("", ALL, {"hide_expired": False})
    assert len(JobSearch.to_table(results)) == 3


def test_escape_markdown():
    assert JobSearch.escape_markdown("11:30~20:00") == r"11:30\~20:00"


def test_main_dashboard_defaults():
    dashboard = MainDashboard()
    assert dashboard.districts == list(SEOUL_DISTRICTS)
    assert len(dashboard.TABS) == 4
    assert dashboard.DEFAULT_DISTRICT in dashboard.districts


# ── 검색 개선 ──────────────────────────────────────────────
def test_split_keywords():
    assert JobSearch.split_keywords("  개발  강남 ") == ["개발", "강남"]
    assert JobSearch.split_keywords("") == []


def test_search_with_several_words(searcher):
    # 예전에는 '회계 사무원'처럼 띄어 쓴 검색어가 0건이었다
    assert [j.company for j in searcher.search("다라 사무원", ALL, {"hide_expired": False})] == ["다라회계"]
    assert searcher.search("다라 개발", ALL, {"hide_expired": False}) == []


def test_follow_map_selection_keeps_all_on_first_visit():
    state = {}
    JobSearch.follow_map_selection(state, "강남구")
    assert JobSearch.AREA_KEY not in state  # 처음엔 '전체' 그대로


def test_follow_map_selection_changes_area_when_map_changes():
    state = {}
    JobSearch.follow_map_selection(state, "강남구")
    JobSearch.follow_map_selection(state, "마포구")
    assert state[JobSearch.AREA_KEY] == "마포구"
    state[JobSearch.AREA_KEY] = "전체"          # 사용자가 직접 '전체'로 바꾸면
    JobSearch.follow_map_selection(state, "마포구")
    assert state[JobSearch.AREA_KEY] == "전체"  # 지도 선택이 그대로면 덮어쓰지 않음


def test_sort_by_headcount_puts_expired_last(make_job):
    jobs = [
        make_job(company="A", headcount="1", deadline="2099-12-31"),
        make_job(company="B", headcount="9", deadline="2000-01-01"),   # 마감
        make_job(company="C", headcount="5", deadline="2099-12-31"),
    ]
    assert [j.company for j in JobSearch.sort_jobs(jobs, "모집인원 많은순")] == ["C", "A", "B"]
    assert [j.company for j in JobSearch.sort_jobs(jobs, "회사명순")] == ["A", "C", "B"]


def test_unknown_sort_falls_back_to_deadline(make_job):
    jobs = [make_job(company="늦음", deadline="2099-12-31"), make_job(company="빠름", deadline="2099-01-01")]
    assert [j.company for j in JobSearch.sort_jobs(jobs, "없는 기준")] == ["빠름", "늦음"]


def test_table_hides_status_column_when_nothing_expired(searcher):
    open_only = searcher.search("", ALL, {"hide_expired": True})
    assert "상태" not in JobSearch.to_table(open_only).columns
    with_expired = searcher.search("", ALL, {"hide_expired": False})
    assert list(JobSearch.to_table(with_expired).columns) == list(JobSearch.TABLE_COLUMNS)


def test_badges(make_job):
    open_job = make_job(deadline="2099-12-31", career="신입")
    texts = [text for _, text in JobSearch.badges(open_job)]
    assert texts[0] == "모집중" and "신입 가능" in texts
    assert JobSearch.badges(make_job(deadline="2000-01-01"))[0] == ("gray", "마감")

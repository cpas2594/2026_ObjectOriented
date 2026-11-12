"""models/ : JobPosting 테스트."""
import pytest

from jobdash import JobPosting


def test_normalize_and_parse():
    assert JobPosting.normalize_text("  a \n b ") == "a b"
    assert JobPosting.normalize_text("nan") == ""
    assert JobPosting.parse_int("1,200명") == 1200
    assert JobPosting.parse_int("") == 0


def test_from_row_is_class_method():
    job = JobPosting.from_row({"company": "B사", "title": "회계", "district": "중구"})
    assert job.company == "B사" and job.get_district() == "중구"
    assert job.job_type == "기타"


def test_real_data_formats():
    job = JobPosting(company="A", title="B", district="중구",
                     job_type="배송?납품 운전원(납품영업 포함)(624102)",
                     deadline="채용시까지  26-11-15", salary="시급10,320원 이상,")
    assert job.job_type == "배송·납품 운전원(납품영업 포함)"
    assert job.job_code == "624102" and job.job_group == "운전·운송직"
    assert job.deadline == "2026-11-15" and job.deadline_text == "2026-11-15 (채용시까지)"
    assert job.salary == "시급10,320원 이상"


def test_employment_categories(make_job):
    assert make_job().employment_category == "정규직"
    part = make_job(employment="기간의 정함이 없는 근로계약(시간(선택)제)/ 파견근로 비희망")
    assert part.employment_category == "시간제" and not part.is_regular()
    contract = make_job(employment="기간의 정함이 있는 근로계약12 개월/ 파견근로 비희망")
    assert contract.employment_category == "계약직"


def test_career_and_flags(make_job):
    assert make_job(career="관계없음").career_category == "무관"
    assert make_job(career="경력").career_category == "경력"
    assert make_job().is_it_job() and make_job().is_college_or_above()
    assert not make_job(job_code="550102").is_it_job()


def test_encapsulation_read_only(make_job):
    with pytest.raises(AttributeError):
        make_job().company = "바꾸기"


def test_matches_filter_ignores_all(make_job):
    job = make_job()
    assert job.matches_filter(job_type="전체", career="신입", district="강남구")
    assert job.matches_filter(job_group="정보통신 연구개발·공학기술직")
    assert not job.matches_filter(district="마포구")


def test_keyword_it_uses_job_code(make_job):
    it_job = make_job()  # 직종코드 133200 → 정보통신
    kitchen = make_job(
        title="주방 보조원 채용", job_type="주방 보조원(일반 음식점)", job_code="531000",
        description="장소: 송파구 중대로 135, IT벤처타워 / 접수: jobfair.incruit.com",
    )
    for kw in ("IT", "it", " It "):
        assert it_job.matches_keyword(kw)
        assert not kitchen.matches_keyword(kw)


def test_keyword_searches_job_type_and_group(make_job):
    job = make_job(title="직원 모집", job_type="주방 보조원(일반 음식점)", job_code="531000")
    assert job.matches_keyword("보조원")          # 직종명
    assert job.matches_keyword("음식 서비스직")    # 직종 분류
    assert not job.matches_keyword("요양")


def test_keyword_english_whole_word(make_job):
    job = make_job(title="Java 백엔드 개발자", description="문의: submit@corp.com, SQL가능자")
    assert job.matches_keyword("java")
    assert job.matches_keyword("SQL")       # 뒤에 한글이 붙어도 허용
    assert not job.matches_keyword("jav")   # 단어 일부는 제외
    assert not job.matches_keyword("mit")   # 'submit' 안의 글자는 제외

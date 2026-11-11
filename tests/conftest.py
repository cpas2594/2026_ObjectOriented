"""여러 테스트 파일에서 함께 쓰는 준비 코드."""
import pytest

from jobdash import JobPosting


@pytest.fixture
def make_job():
    """기본값이 채워진 JobPosting을 만든다. 필요한 값만 바꿔서 쓴다."""
    def _make(**overrides):
        values = dict(
            company="A사", title="개발자 채용", job_type="응용 소프트웨어 개발자",
            job_code="133200", career="신입", education="대졸(4년)",
            employment="기간의 정함이 없는 근로계약/ 파견근로 비희망",
            headcount="2", district="강남구",
        )
        values.update(overrides)
        return JobPosting(**values)
    return _make

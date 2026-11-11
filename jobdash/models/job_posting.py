"""채용공고 1건을 표현하는 JobPosting 클래스.

담당: 김규린

적용 개념
- Objects and Classes: 채용공고 1건 = 객체 1개
- Constructors: __init__()에서 값을 정제해 초기화
- Class Variables / Class Methods / Static Methods:
    required_fields, from_row(), normalize_text()
- Encapsulation: 속성은 _(언더스코어)로 감추고 property와 메서드로만 조회
"""
from __future__ import annotations

import re
from typing import Optional

from .job_codes import IT_GROUP_CODES, IT_KEYWORDS, job_group_name


class JobPosting:
    # ── 클래스 변수: 모든 객체가 공유하는 값 ─────────────────────────
    # 이 값이 비어 있으면 객체를 만들지 않는다.
    required_fields = ("company", "title", "district")

    # 생성자가 받는 전체 필드 (from_row에서 사용)
    fields = (
        "company", "title", "job_type", "career", "education", "salary",
        "employment", "headcount", "deadline", "district", "description", "job_code",
    )

    # 한국고용직업분류(KECO) 중분류: 직종코드 앞 두 자리 → 직종 분류 이름

    COLLEGE_KEYWORDS = ("대졸", "대학", "학사", "석사", "박사")

    # ── 생성자 ──────────────────────────────────────────────────────
    def __init__(
        self,
        company: str,
        title: str,
        job_type: str = "",
        career: str = "",
        education: str = "",
        salary: str = "",
        employment: str = "",
        headcount=0,
        deadline: str = "",
        district: str = "",
        description: str = "",
        job_code: str = "",
    ) -> None:
        self._company = self.normalize_text(company)
        self._title = self.normalize_text(title)
        self._job_code = re.sub(r"\D", "", str(job_code or ""))
        if not self._job_code:  # 코드 열이 없으면 '직종명(550102)'에서 코드를 꺼낸다
            m = re.search(r"\((\d{6})\)\s*$", str(job_type or ""))
            self._job_code = m.group(1) if m else ""
        self._job_type = self.clean_job_type(job_type) or "기타"
        self._career = self.normalize_text(career)
        self._education = self.normalize_text(education) or "학력무관"
        self._salary = self.normalize_text(salary).rstrip(", ")
        self._employment = self.normalize_text(employment)
        self._headcount = self.parse_int(headcount)
        self._until_filled = "채용시까지" in str(deadline or "")
        self._deadline = self.parse_deadline(deadline)
        self._district = self.normalize_text(district)
        self._description = self.normalize_text(description)

    # ── 클래스 메서드: 다른 형태의 입력으로 객체를 만드는 "대체 생성자" ──
    @classmethod
    def from_row(cls, row: dict) -> "JobPosting":
        """정리된 CSV 한 행(dict)으로 JobPosting 객체를 만든다."""
        return cls(**{name: row.get(name, "") for name in cls.fields})

    # ── 정적 메서드: 객체 상태와 무관한 유틸리티 ──────────────────────
    @staticmethod
    def normalize_text(value) -> str:
        """공백·줄바꿈을 정리하고, 결측치 표기는 빈 문자열로 바꾼다."""
        if value is None:
            return ""
        text = re.sub(r"\s+", " ", str(value)).strip()
        if text.lower() in {"nan", "none", "null", "-", "n/a"}:
            return ""
        return text

    @staticmethod
    def clean_job_type(value) -> str:
        """'재가 요양보호사(550102)' → '재가 요양보호사'. 깨진 가운뎃점(?)도 복원."""
        text = JobPosting.normalize_text(value)
        text = re.sub(r"\s*\(\d{6}\)$", "", text)
        return re.sub(r"(?<=[가-힣A-Za-z])\?(?=[가-힣A-Za-z])", "·", text)

    @staticmethod
    def parse_deadline(value) -> str:
        """'채용시까지  26-11-15' / '26-11-30' → '2026-11-15'. 날짜가 없으면 빈 문자열."""
        text = str(value or "")
        m = re.search(r"(\d{2,4})[-./](\d{1,2})[-./](\d{1,2})", text)
        if not m:
            return ""
        year = m.group(1) if len(m.group(1)) == 4 else f"20{m.group(1)}"
        return f"{year}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    @staticmethod
    def parse_int(value) -> int:
        """'3명', '00', '1,200' 같은 값을 정수로 바꾼다. 숫자가 없으면 0."""
        digits = re.sub(r"[^\d]", "", str(value or ""))
        return int(digits) if digits else 0

    # ── 캡슐화: 읽기 전용 property ────────────────────────────────────
    @property
    def company(self) -> str:
        return self._company

    @property
    def title(self) -> str:
        return self._title

    @property
    def job_type(self) -> str:
        return self._job_type

    @property
    def career(self) -> str:
        return self._career

    @property
    def education(self) -> str:
        return self._education

    @property
    def salary(self) -> str:
        return self._salary

    @property
    def employment(self) -> str:
        return self._employment

    @property
    def headcount(self) -> int:
        return self._headcount

    @property
    def deadline(self) -> str:
        return self._deadline

    @property
    def deadline_text(self) -> str:
        if not self._deadline:
            return "채용시까지" if self._until_filled else "미정"
        return f"{self._deadline} (채용시까지)" if self._until_filled else self._deadline

    @property
    def job_code(self) -> str:
        return self._job_code

    @property
    def job_group(self) -> str:
        """직종코드 앞 두 자리로 찾은 직종 분류. 코드가 없으면 '기타'."""
        return job_group_name(self._job_code)

    @property
    def description(self) -> str:
        return self._description

    def get_district(self) -> str:
        return self._district

    # ── 정규화된 분류값 (필터·통계용) ─────────────────────────────────
    @property
    def career_category(self) -> str:
        """원본 경력 표기를 '신입' / '경력' / '무관' 셋 중 하나로 묶는다."""
        text = self._career
        if not text or "무관" in text or "관계없" in text:
            return "무관"
        if "신입" in text:
            return "신입"
        return "경력"

    @property
    def employment_category(self) -> str:
        """원본 고용형태를 '정규직' / '시간제' / '계약직' / '기타'로 묶는다.

        정규직: 기간의 정함이 없는 근로계약(전일제)
        시간제: 기간의 정함이 없는 근로계약(시간(선택)제)
        계약직: 기간의 정함이 있는 근로계약 (시간제 포함)
        """
        text = self._employment
        # 순서 주의: '기간의 정함이 없는 근로계약'에도 '계약'이 들어 있다.
        if "기간의 정함이 없는" in text:
            return "시간제" if "시간" in text.split("/")[0] else "정규직"
        if "비정규" in text or "계약" in text or "기간의 정함이 있는" in text:
            return "계약직"
        if "정규" in text:
            return "정규직"
        return "기타"

    # ── 판정 메서드 ──────────────────────────────────────────────────
    def is_entry_level(self) -> bool:
        """신입 지원 가능 여부 (신입 또는 경력무관)."""
        return self.career_category in ("신입", "무관")

    def is_regular(self) -> bool:
        return self.employment_category == "정규직"

    def is_college_or_above(self) -> bool:
        """대졸(전문대 포함) 이상 요구 여부."""
        return any(k in self._education for k in self.COLLEGE_KEYWORDS)

    def is_it_job(self) -> bool:
        if self._job_code:
            return self._job_code[:2] in IT_GROUP_CODES
        return any(k in self._job_type for k in IT_KEYWORDS)

    def is_valid(self) -> bool:
        return all(getattr(self, f"_{name}") for name in self.required_fields)

    def matches_filter(
        self,
        job_type: Optional[str] = None,
        career: Optional[str] = None,
        employment: Optional[str] = None,
        district: Optional[str] = None,
        job_group: Optional[str] = None,
    ) -> bool:
        """선택된 조건과 모두 일치하면 True. None 또는 '전체'는 조건에서 제외."""
        checks = (
            (job_group, self.job_group),
            (job_type, self._job_type),
            (career, self.career_category),
            (employment, self.employment_category),
            (district, self._district),
        )
        return all(
            wanted in (None, "", "전체") or wanted == actual
            for wanted, actual in checks
        )

    def matches_keyword(self, keyword: str) -> bool:
        """회사명·채용제목·직무내용에 검색어가 들어 있으면 True."""
        keyword = self.normalize_text(keyword).lower()
        if not keyword:
            return True
        haystack = f"{self._company} {self._title} {self._description}".lower()
        return keyword in haystack

    def duplicate_key(self) -> tuple:
        """같은 공고인지 판단할 때 쓰는 키 (중복 제거용)."""
        return (self._company, self._title, self._district, self._deadline)

    # ── 출력 ──────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "회사명": self._company,
            "채용제목": self._title,
            "자치구": self._district,
            "직종 분류": self.job_group,
            "직종": self._job_type,
            "경력": self._career or "무관",
            "학력": self._education,
            "급여": self._salary,
            "고용형태": self.employment_category,
            "계약조건": self._employment.split("/")[0].strip(),
            "모집인원": self._headcount,
            "마감일": self.deadline_text,
        }

    def __repr__(self) -> str:
        return f"JobPosting({self._company!r}, {self._title!r}, {self._district!r})"

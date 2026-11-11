"""사이드바: 데이터 선택과 필터.

담당: 김규린
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd
import streamlit as st

from ..config import ALL, CAREER_OPTIONS, EMPLOYMENT_OPTIONS, REAL_DATA, SAMPLE_DATA
from ..data_processing import JobDataManager
from .resources import load_manager


@dataclass(frozen=True)
class Filters:
    """사이드바에서 고른 필터 조건 묶음."""
    job_group: str = ALL
    job_type: str = ALL
    career: str = ALL
    employment: str = ALL

    def as_dict(self) -> dict:
        return asdict(self)


def render_data_source() -> JobDataManager:
    """업로드 파일 → data/jobs.csv → 샘플 데이터 순으로 데이터를 고른다."""
    st.sidebar.header("데이터")
    uploaded = st.sidebar.file_uploader("채용정보 CSV 올리기", type="csv")
    if uploaded is not None:
        source, name = uploaded.getvalue(), uploaded.name
    elif REAL_DATA.exists():
        source, name = REAL_DATA.read_bytes(), REAL_DATA.name
    else:
        source, name = SAMPLE_DATA.read_bytes(), "샘플 데이터"

    try:
        manager = load_manager(source)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    st.sidebar.caption(f"{name} · 공고 {len(manager):,}건 사용")
    with st.sidebar.expander("데이터 정제 결과"):
        st.table(pd.Series(manager.load_report, name="건수"))
    return manager


def render_filters(manager: JobDataManager) -> Filters:
    st.sidebar.header("필터")
    job_group = st.sidebar.selectbox("직종 분류", [ALL] + manager.unique_values("job_group"))
    group_jobs = manager.filter_jobs(job_group=job_group)
    job_type = st.sidebar.selectbox("세부 직종", [ALL] + manager.unique_values("job_type", group_jobs))
    career = st.sidebar.selectbox("경력", [ALL, *CAREER_OPTIONS])
    employment = st.sidebar.selectbox(
        "고용형태", [ALL, *EMPLOYMENT_OPTIONS],
        help="정규직: 기간의 정함이 없는 근로계약 / 시간제: 같은 계약의 시간(선택)제 / "
             "계약직: 기간의 정함이 있는 근로계약",
    )
    return Filters(job_group, job_type, career, employment)

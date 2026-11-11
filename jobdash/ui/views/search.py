"""채용공고 검색 화면: 검색어·필터·지역으로 실제 공고 목록과 상세 정보 조회.

담당: 한예승
"""
import pandas as pd
import streamlit as st

from ...config import ALL
from ...data_processing import JobDataManager
from ...models import JobPosting

MAX_DETAIL_OPTIONS = 300
DETAIL_FIELDS = ("직종 분류", "직종", "경력", "학력", "고용형태", "계약조건", "급여", "모집인원")


def render(manager: JobDataManager, filters: dict, districts: list[str]) -> None:
    c1, c2 = st.columns([3, 1])
    keyword = c1.text_input("검색어", placeholder="회사명, 채용제목, 직무내용")
    area = c2.selectbox("지역", [ALL] + districts)
    results = manager.search_jobs(keyword, district=area, **filters)

    st.write(f"검색 결과 **{len(results):,}건**")
    if not results:
        return

    st.dataframe(pd.DataFrame([job.to_dict() for job in results]),
                 hide_index=True, width="stretch", height=420)

    pick = st.selectbox(
        "상세 보기", range(min(len(results), MAX_DETAIL_OPTIONS)),
        format_func=lambda i: f"{results[i].company} | {results[i].title}",
    )
    _render_detail(results[pick])


def _render_detail(job: JobPosting) -> None:
    with st.container(border=True):
        st.subheader(job.title)
        st.write(f"**{job.company}** · {job.get_district()} · 마감 {job.deadline_text}")
        info = job.to_dict()
        cols = st.columns(3)
        for i, key in enumerate(DETAIL_FIELDS):
            cols[i % 3].markdown(f"**{key}**  \n{info[key]}")
        if job.description:
            st.markdown(f"**직무내용**  \n{job.description}")

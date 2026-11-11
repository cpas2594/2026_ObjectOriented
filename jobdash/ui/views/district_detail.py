"""자치구 상세 화면: 선택한 구의 공고 수와 직종·경력·고용형태·학력 분포.

담당: 박수연
"""
import streamlit as st

from ...analysis import DistrictAnalyzer
from ...data_processing import JobDataManager
from ..charts import bar_chart, donut_chart, metric_row


def render(manager: JobDataManager, filtered_jobs: list, districts: list[str]) -> None:
    district = st.selectbox("자치구", districts, key="district")
    district_jobs = manager.filter_jobs(district=district, jobs=filtered_jobs)

    if not district_jobs:
        st.info(f"{district}에는 현재 필터에 맞는 공고가 없습니다. 왼쪽 필터를 넓혀 보세요.")
        return

    detail = DistrictAnalyzer(district_jobs, [district]).analyze()
    metric_row(st, detail["summary"])

    dist = detail["distributions"]
    c1, c2 = st.columns(2)
    c1.plotly_chart(bar_chart(dist["직종 분류"], "직종 분류 상위 10개", horizontal=True), width="stretch")
    c2.plotly_chart(bar_chart(dist["직종"], "세부 직종 상위 10개", horizontal=True), width="stretch")

    for col, name in zip(st.columns(3), ("경력", "고용형태", "학력")):
        col.plotly_chart(donut_chart(dist[name], name), width="stretch")

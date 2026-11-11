"""자치구 비교 화면: 선택한 구와 서울 전체(또는 다른 구)의 비율 비교.

담당: 유해린
"""
import pandas as pd
import streamlit as st

from ...analysis import ComparisonAnalyzer
from ...config import SEOUL
from ...data_processing import JobDataManager
from ..charts import comparison_chart


def render(manager: JobDataManager, filtered_jobs: list, districts: list[str]) -> None:
    c1, c2 = st.columns(2)
    base = c1.selectbox("기준 자치구", districts, index=districts.index(st.session_state.district))
    target = c2.selectbox("비교 대상", [SEOUL] + [d for d in districts if d != base])

    base_jobs = manager.filter_jobs(district=base, jobs=filtered_jobs)
    target_jobs = (filtered_jobs if target == SEOUL
                   else manager.filter_jobs(district=target, jobs=filtered_jobs))
    result = ComparisonAnalyzer(base_jobs, target_jobs, base, target).analyze()

    st.caption(f"{base} {result['counts'][0]:,}건 vs {target} {result['counts'][1]:,}건 (현재 필터 적용)")
    cmp_df = pd.DataFrame(result["metrics"])
    st.plotly_chart(comparison_chart(cmp_df, base, target), width="stretch")
    st.dataframe(cmp_df, hide_index=True, width="stretch")

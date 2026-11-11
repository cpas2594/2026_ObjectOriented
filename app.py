"""서울시 일자리 포털 채용 정보 대시보드 (Streamlit).

실행:  streamlit run app.py

이 파일은 화면 전체의 순서만 정한다. 실제 내용은 기능별 폴더에 있다.
- 사이드바(데이터·필터):  jobdash/ui/sidebar.py
- 각 탭 화면:             jobdash/ui/views/
- 데이터 처리:            jobdash/data_processing/
- 통계 계산:              jobdash/analysis/

담당: 한예승 (UI 통합)
"""
import streamlit as st

from jobdash.ui.sidebar import render_data_source, render_filters
from jobdash.ui.views import comparison, district_detail, overview, search

st.set_page_config(page_title="서울시 채용 현황", page_icon="🗺️", layout="wide")

# 1. 데이터와 필터
manager = render_data_source()
filters = render_filters(manager).as_dict()
filtered = manager.filter_jobs(**filters)
districts = list(manager.SEOUL_DISTRICTS)

# 지도에서 고른 자치구를 여러 탭이 함께 쓴다
if "district" not in st.session_state:
    st.session_state.district = "강남구"

# 2. 화면
st.title("서울시 자치구별 채용 현황")
st.caption("서울 일자리 포털 채용정보 기준. 왼쪽 필터를 바꾸면 모든 화면이 함께 바뀝니다.")

tab_map, tab_detail, tab_compare, tab_search = st.tabs(
    ["서울 전체 현황", "자치구 상세", "자치구 비교", "채용공고 검색"]
)
with tab_map:
    overview.render(filtered, districts)
with tab_detail:
    district_detail.render(manager, filtered, districts)
with tab_compare:
    comparison.render(manager, filtered, districts)
with tab_search:
    search.render(manager, filters, districts)

"""대시보드 전체를 조립하는 MainDashboard.

담당: 한예승 (Streamlit UI 통합)
"""
import streamlit as st

from ..config import SEOUL_DISTRICTS
from .sidebar import render_data_source, render_filters
from .views import comparison, district_detail, overview
from .views.search import JobSearch


class MainDashboard:
    """사이드바(데이터·필터)와 탭 4개를 하나의 화면으로 조립하는 객체.

    흐름: run() → 데이터 불러오기 → 필터 적용 → 탭별 화면 그리기
    각 탭의 내용은 담당 모듈/클래스에 맡기고, 이 클래스는 순서와 공유 상태만 관리한다.
    """

    TITLE = "서울시 자치구별 채용 현황"
    TABS = ("서울 전체 현황", "자치구 상세", "자치구 비교", "채용공고 검색")
    DEFAULT_DISTRICT = "강남구"

    def __init__(self):
        self.manager = None        # JobDataManager
        self.filters: dict = {}    # 사이드바에서 고른 조건
        self.filtered: list = []   # 필터가 적용된 JobPosting 목록
        self.districts = list(SEOUL_DISTRICTS)

    def run(self) -> None:
        st.set_page_config(page_title="서울시 채용 현황", page_icon="🗺️", layout="wide")
        self._load_data()
        self._init_state()
        self._render_header()
        self._render_tabs()

    def _load_data(self) -> None:
        """사이드바에서 데이터를 고르고 필터를 적용한다."""
        self.manager = render_data_source()
        self.filters = render_filters(self.manager).as_dict()
        self.filtered = self.manager.filter_jobs(**self.filters)

    def _init_state(self) -> None:
        """지도에서 고른 자치구를 여러 탭이 함께 쓰도록 session_state에 둔다."""
        if "district" not in st.session_state:
            st.session_state.district = self.DEFAULT_DISTRICT

    def _render_header(self) -> None:
        st.title(self.TITLE)

    def _render_tabs(self) -> None:
        tab_map, tab_detail, tab_compare, tab_search = st.tabs(list(self.TABS))
        with tab_map:
            overview.render(self.filtered, self.districts)
        with tab_detail:
            district_detail.render(self.manager, self.filtered, self.districts)
        with tab_compare:
            comparison.render(self.manager, self.filtered, self.districts)
        with tab_search:
            JobSearch(self.manager, self.districts).render(self.filters)

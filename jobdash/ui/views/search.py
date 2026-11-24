"""채용공고 검색 화면: 검색어·필터·지역으로 실제 공고 목록과 상세 정보 조회.

담당: 한예승 (JobSearch)
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ...config import ALL
from ...data_processing import JobDataManager
from ...models import JobPosting


class JobSearch:
    """'채용공고 검색' 탭 하나를 맡는 객체.

    - 검색 자체(조건에 맞는 JobPosting 찾기)는 JobDataManager.search_jobs()에 맡기고,
      이 클래스는 입력 받기 → 결과 표 → 상세 정보 표시만 책임진다. (단일 책임)
    - 표에 보여줄 값은 JobPosting.to_dict()로 받아서, 공고 내부 속성에 직접 의존하지 않는다. (캡슐화)
    """

    # ── 클래스 변수: 모든 JobSearch 객체가 함께 쓰는 설정 ──
    # 결과 표에 보여줄 열 (나머지는 상세 정보에서 확인)
    TABLE_COLUMNS = ("상태", "회사명", "채용제목", "자치구", "직종", "경력", "고용형태", "급여", "마감일")
    # 상세 정보에 4열로 보여줄 항목
    DETAIL_FIELDS = ("급여", "경력", "학력", "모집인원", "직종", "직종 분류", "고용형태", "계약조건")
    # 정렬 기준: 이름 → 정렬 키 (마감 공고는 항상 맨 뒤)
    SORT_OPTIONS = {
        "마감 임박순": lambda job: (job.is_expired(), job.deadline == "", job.deadline),
        "모집인원 많은순": lambda job: (job.is_expired(), -job.headcount),
        "회사명순": lambda job: (job.is_expired(), job.company),
    }
    AREA_KEY = "search_area"                 # 지역 선택 상자의 session_state 키
    LAST_MAP_KEY = "search_last_district"    # 검색 탭이 마지막으로 본 '지도에서 고른 구'
    ROW_HEIGHT, MAX_TABLE_HEIGHT = 35, 420

    def __init__(self, manager: JobDataManager, districts: list[str]):
        self._manager = manager
        self._districts = list(districts)

    # ---------- 검색 (화면과 무관한 부분: 테스트 가능) ----------
    def search(self, keyword: str = "", area: str = ALL, filters: dict | None = None) -> list[JobPosting]:
        """검색어 + 사이드바 필터 + 지역을 함께 적용한 공고 목록.

        검색어를 띄어쓰기로 나눠서, 모든 단어가 들어 있는 공고만 남긴다.
        예) '요양 야간' → '요양'도 있고 '야간'도 있는 공고
        """
        words = self.split_keywords(keyword)
        first = words[0] if words else ""
        results = self._manager.search_jobs(first, district=area, **(filters or {}))
        return [job for job in results if all(job.matches_keyword(w) for w in words[1:])]

    @staticmethod
    def split_keywords(keyword: str) -> list[str]:
        """'  개발  강남 ' → ['개발', '강남']"""
        return (keyword or "").split()

    @classmethod
    def sort_jobs(cls, results: list[JobPosting], order: str) -> list[JobPosting]:
        """SORT_OPTIONS의 기준으로 정렬한 새 목록. 모르는 기준이면 마감 임박순."""
        key = cls.SORT_OPTIONS.get(order, cls.SORT_OPTIONS["마감 임박순"])
        return sorted(results, key=key)

    @classmethod
    def follow_map_selection(cls, state, map_district: str) -> None:
        """지도(또는 자치구 상세 탭)에서 다른 구를 고르면 검색 탭 지역도 그 구로 바꾼다.

        처음 열었을 때는 '전체'로 두고, 그 뒤 고른 구가 바뀐 경우에만 따라간다.
        state는 st.session_state (테스트에서는 일반 dict도 됨).
        """
        if cls.LAST_MAP_KEY not in state:
            state[cls.LAST_MAP_KEY] = map_district
            return
        if state[cls.LAST_MAP_KEY] != map_district:
            state[cls.LAST_MAP_KEY] = map_district
            state[cls.AREA_KEY] = map_district

    @staticmethod
    def summary_text(results: list[JobPosting]) -> str:
        """'검색 결과 N건 (마감 M건 포함)' 문구."""
        expired = sum(1 for job in results if job.is_expired())
        text = f"검색 결과 **{len(results):,}건**"
        return text + (f" (마감 {expired:,}건 포함)" if expired else "")

    @classmethod
    def to_table(cls, results: list[JobPosting]) -> pd.DataFrame:
        """결과 표. 마감 공고가 하나도 없으면 '상태' 열은 뺀다(전부 '모집중'이라 의미 없음)."""
        columns = list(cls.TABLE_COLUMNS)
        if not any(job.is_expired() for job in results):
            columns.remove("상태")
        rows = [{c: job.to_dict()[c] for c in columns} for job in results]
        return pd.DataFrame(rows, columns=columns)

    @staticmethod
    def badges(job: JobPosting) -> list[tuple[str, str]]:
        """상세 정보 맨 위에 붙일 (색, 글자) 목록."""
        items = [("gray", "마감") if job.is_expired() else ("green", "모집중")]
        items.append(("blue", job.employment_category))
        if job.is_entry_level():
            items.append(("violet", "신입 가능"))
        return items

    @staticmethod
    def escape_markdown(value) -> str:
        """마크다운에서 '~'가 취소선이 되지 않도록 이스케이프한다. ('11:30~20:00' 등)"""
        return str(value).replace("~", r"\~")

    # ---------- 화면 그리기 ----------
    def render(self, filters: dict) -> None:
        keyword, area, order = self._render_inputs()
        results = self.sort_jobs(self.search(keyword, area, filters), order)

        st.markdown(self.summary_text(results))
        if not results:
            st.info(
                "조건에 맞는 공고가 없어요. 검색어를 줄이거나, 지역이나 왼쪽 필터를 넓혀 보세요.",
                icon=":material/search_off:",
            )
            return

        condition = (keyword, area, order, tuple(sorted(filters.items())))
        selected = self._render_table(results, condition)
        if selected is not None:
            self._render_detail(selected)

    def _render_inputs(self) -> tuple[str, str, str]:
        c1, c2, c3 = st.columns([3, 1, 1])
        keyword = c1.text_input(
            "검색어", placeholder="예: 요양 야간, 바리스타 신입 (띄어 쓰면 모든 단어 포함)",
        )
        self.follow_map_selection(st.session_state, st.session_state.get("district", ""))
        area = c2.selectbox("지역", [ALL] + self._districts, key=self.AREA_KEY)
        order = c3.selectbox("정렬", list(self.SORT_OPTIONS))
        return keyword, area, order

    def _render_table(self, results: list[JobPosting], condition: tuple) -> JobPosting | None:
        """결과 표를 그리고, 사용자가 클릭한 공고를 돌려준다(없으면 None).

        검색 조건이 바뀌면 key도 바뀌어서 이전 선택(다른 목록의 행 번호)이 초기화된다.
        결과가 적으면 표 높이도 줄여서 빈 공간이 생기지 않게 한다.
        """
        height = min(self.MAX_TABLE_HEIGHT, self.ROW_HEIGHT * (len(results) + 1) + 3)
        event = st.dataframe(
            self.to_table(results),
            hide_index=True, width="stretch", height=height,
            on_select="rerun", selection_mode="single-cell",
            key=f"search_table_{hash(condition)}",
            column_config={
                "상태": st.column_config.TextColumn(width="small"),
                "회사명": st.column_config.TextColumn(width="medium"),
                "채용제목": st.column_config.TextColumn(width="large"),
                "자치구": st.column_config.TextColumn(width="small"),
                "마감일": st.column_config.TextColumn(width="medium"),
            },
        )
        cells = event.selection.cells if event else []  # [(행 번호, 열 이름)]
        return results[cells[0][0]] if cells else None

    def _render_detail(self, job: JobPosting) -> None:
        md = self.escape_markdown
        with st.container(border=True):
            st.markdown(" ".join(f":{color}-badge[{text}]" for color, text in self.badges(job)))
            st.subheader(md(job.title), anchor=False)
            st.caption(f"{md(job.company)} · {job.get_district()} · 마감 {job.deadline_text}")

            info = job.to_dict()
            info["모집인원"] = f"{info['모집인원']}명" if info["모집인원"] else "-"
            cols = st.columns(4)
            for i, key in enumerate(self.DETAIL_FIELDS):
                with cols[i % 4]:
                    st.caption(key)
                    st.markdown(md(info[key]) or "-")

            if job.description:
                st.divider()
                st.caption("직무내용")
                st.markdown(md(job.description))


def render(manager: JobDataManager, filters: dict, districts: list[str]) -> None:
    """다른 탭과 같은 모양(views.xxx.render)으로도 부를 수 있게 남겨둔 함수."""
    JobSearch(manager, districts).render(filters)

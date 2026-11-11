"""서울 전체 현황 화면: 자치구별 지도와 상위 자치구.

담당: 김규린
"""
import pandas as pd
import streamlit as st

from ...analysis import DistrictAnalyzer
from ..charts import district_map, metric_row


def render(filtered_jobs: list, districts: list[str]) -> None:
    overview = DistrictAnalyzer(filtered_jobs, districts).analyze()
    metric_row(st, overview["summary"])

    metric = st.radio("지도 기준", ["공고 수", "모집인원"], horizontal=True)
    map_df = pd.DataFrame([{"자치구": d, **s} for d, s in overview["by_district"].items()])

    event = st.plotly_chart(district_map(map_df, metric), width="stretch",
                            on_select="rerun", key="seoul_map")
    _handle_map_click(event, map_df, districts)
    st.caption("자치구를 클릭하면 '자치구 상세' 탭에 그 구가 선택됩니다.")

    top = map_df.sort_values(metric, ascending=False).head(5)
    unit = "건" if metric == "공고 수" else "명"
    ranking = " / ".join(f"{row['자치구']} {row[metric]:,}{unit}" for _, row in top.iterrows())
    st.write(f"**{metric} 상위 5개 자치구**: {ranking}")


def _handle_map_click(event, map_df: pd.DataFrame, districts: list[str]) -> None:
    """지도에서 클릭한 자치구를 session_state에 저장해 다른 탭과 공유한다."""
    points = event.get("selection", {}).get("points", []) if event else []
    if not points:
        return
    clicked = points[0].get("location")
    if clicked is None and "point_index" in points[0]:
        clicked = map_df.iloc[points[0]["point_index"]]["자치구"]
    if clicked in districts and clicked != st.session_state.district:
        st.session_state.district = clicked
        st.toast(f"{clicked}를 선택했습니다. '자치구 상세' 탭에서 확인하세요.")

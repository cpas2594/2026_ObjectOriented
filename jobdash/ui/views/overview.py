"""서울 전체 현황 화면: 자치구별 지도와 상위 자치구.

담당: 김규린
"""
import pandas as pd
import streamlit as st

from ...analysis import DistrictAnalyzer
from ..charts import MAP_METRICS, district_map, metric_row


def render(filtered_jobs: list, districts: list[str]) -> None:
    overview = DistrictAnalyzer(filtered_jobs, districts).analyze()
    metric_row(st, overview["summary"])

    metric = st.radio("지도 기준", list(MAP_METRICS), horizontal=True)
    map_df = pd.DataFrame([{"자치구": d, **s} for d, s in overview["by_district"].items()])

    event = st.plotly_chart(district_map(map_df, metric), width="stretch",
                            on_select="rerun", key=f"seoul_map_{metric}")
    _handle_map_click(event, map_df, districts)
    st.caption("자치구를 클릭하면 '자치구 상세' 탭에 그 구가 선택됩니다.")

    top = map_df.sort_values(metric, ascending=False).head(5)
    unit = MAP_METRICS[metric][1]
    ranking = " / ".join(f"{row['자치구']} {row[metric]:,g}{unit}" for _, row in top.iterrows())
    st.write(f"**{metric} 상위 5개 자치구**: {ranking}")


LAST_CLICK_KEY = "map_last_click"   # 마지막으로 처리한 지도 클릭


def _handle_map_click(event, map_df: pd.DataFrame, districts: list[str]) -> None:
    """지도에서 클릭한 자치구를 session_state에 저장해 다른 탭과 공유한다.

    Plotly 차트는 선택을 계속 기억하므로, 새로 클릭했을 때만 반영한다.
    (안 그러면 자치구 상세에서 구를 바꿔도 지도 선택으로 되돌아간다)
    """
    points = event.get("selection", {}).get("points", []) if event else []
    if not points:
        st.session_state.pop(LAST_CLICK_KEY, None)   # 선택이 해제되면 기록도 지움
        return
    clicked = points[0].get("location")
    if clicked is None and "point_index" in points[0]:
        clicked = map_df.iloc[points[0]["point_index"]]["자치구"]
    if clicked not in districts or clicked == st.session_state.get(LAST_CLICK_KEY):
        return                                        # 이미 처리한 클릭
    st.session_state[LAST_CLICK_KEY] = clicked
    if clicked != st.session_state.district:
        st.session_state.district = clicked
        st.toast(f"{clicked}를 선택했습니다. '자치구 상세' 탭에서 확인하세요.")

"""여러 화면에서 함께 쓰는 Plotly 차트 생성 함수."""
import pandas as pd
import plotly.express as px

from ..config import PRIMARY_COLOR, SECONDARY_COLOR
from .resources import load_geojson


def bar_chart(counts: dict, title: str, horizontal: bool = False):
    """{항목: 개수} dict로 막대그래프를 만든다."""
    df = pd.DataFrame({"항목": list(counts), "공고 수": list(counts.values())})
    if horizontal:
        fig = px.bar(df.iloc[::-1], x="공고 수", y="항목", orientation="h", title=title)
    else:
        fig = px.bar(df, x="항목", y="공고 수", title=title)
    fig.update_traces(marker_color=PRIMARY_COLOR)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320,
                      yaxis_title=None, xaxis_title=None)
    return fig


def donut_chart(counts: dict, title: str):
    fig = px.pie(names=list(counts), values=list(counts.values()), title=title, hole=0.45,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300)
    return fig


def district_map(map_df: pd.DataFrame, metric: str):
    """자치구별 값이 클수록 진하게 칠한 서울 지도."""
    fig = px.choropleth(
        map_df,
        geojson=load_geojson(),
        locations="자치구",
        featureidkey="properties.name",
        color=metric,
        color_continuous_scale="Blues",
        hover_data={"자치구": True, "공고 수": True, "모집인원": True},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560, dragmode=False)
    return fig


def comparison_chart(cmp_df: pd.DataFrame, base: str, target: str):
    long_df = cmp_df.melt(id_vars="지표", value_vars=[base, target],
                          var_name="대상", value_name="비율(%)")
    fig = px.bar(long_df, x="지표", y="비율(%)", color="대상", barmode="group",
                 color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR], text="비율(%)")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=380,
                      yaxis_range=[0, 100], xaxis_title=None)
    return fig


def metric_row(container, summary: dict) -> None:
    """공고 수·모집인원·신입 가능 수를 한 줄에 보여준다."""
    c1, c2, c3 = container.columns(3)
    c1.metric("채용공고", f"{summary['공고 수']:,}건")
    c2.metric("모집인원", f"{summary['모집인원']:,}명")
    c3.metric("신입 지원 가능", f"{summary['신입 가능']:,}건")

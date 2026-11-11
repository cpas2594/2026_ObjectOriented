"""데이터·지도 파일을 한 번만 읽도록 캐시하는 함수들."""
import json

import streamlit as st

from ..config import GEOJSON
from ..data_processing import JobDataManager


@st.cache_resource(show_spinner="채용 데이터를 불러오는 중…")
def load_manager(source: bytes) -> JobDataManager:
    return JobDataManager.from_csv(source)


@st.cache_data
def load_geojson() -> dict:
    return json.loads(GEOJSON.read_text(encoding="utf-8"))

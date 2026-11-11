"""프로젝트 전체에서 함께 쓰는 설정값."""
from pathlib import Path

# 경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REAL_DATA = DATA_DIR / "jobs.csv"            # 실제 데이터
SAMPLE_DATA = DATA_DIR / "sample_jobs.csv"   # 실제 데이터가 없을 때 쓰는 샘플
GEOJSON = DATA_DIR / "seoul_districts.geojson"

# 서울 25개 자치구
SEOUL_DISTRICTS = (
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구",
    "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구",
    "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구",
    "은평구", "종로구", "중구", "중랑구",
)

# 화면에서 쓰는 선택지 이름
ALL = "전체"
SEOUL = "서울 전체"
CAREER_OPTIONS = ("신입", "경력", "무관")
EMPLOYMENT_OPTIONS = ("정규직", "시간제", "계약직", "기타")

# 색상
PRIMARY_COLOR = "#1f4e79"
SECONDARY_COLOR = "#9ec5e8"

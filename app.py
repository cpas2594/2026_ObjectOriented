"""서울시 일자리 포털 채용 정보 대시보드 (Streamlit).

실행:  streamlit run app.py

화면 조립은 MainDashboard(jobdash/ui/dashboard.py)가 맡는다.
- 사이드바(데이터·필터):  jobdash/ui/sidebar.py
- 각 탭 화면:             jobdash/ui/views/  (검색 탭은 JobSearch)
- 데이터 처리:            jobdash/data_processing/
- 통계 계산:              jobdash/analysis/

담당: 한예승 (UI 통합)
"""
from jobdash.ui.dashboard import MainDashboard

MainDashboard().run()

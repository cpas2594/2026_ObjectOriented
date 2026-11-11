# 서울시 일자리 포털 채용 정보 대시보드

서울시 일자리 포털 채용 정보 데이터를 활용해 서울시 25개 자치구의 채용 현황을 분석하고 시각화하는 Streamlit 대시보드입니다. (2026 객체지향프로그래밍 팀 프로젝트)

## 실행 방법

```bash
git clone https://github.com/cpas2594/2026_ObjectOriented.git
cd 2026_ObjectOriented
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501`이 열립니다.

실제 데이터 파일(`data/jobs.csv`)이 없으면 샘플 데이터(`data/sample_jobs.csv`)로 실행됩니다. 샘플 데이터는 `python scripts/make_sample_data.py`로 다시 만들 수 있습니다.

## 사용 데이터

- 데이터: 서울 일자리 포털 채용정보 CSV (`data/jobs.csv`, 39,752행, CP949 인코딩)
- 사용 열: 기업명, 채용제목, 경력, 마감일자, 근무지역, 최소학력, 모집직종, 직종코드, 직무내용, 고용형태, 모집인원, 임금조건
- 지도: [southkorea/seoul-maps](https://github.com/southkorea/seoul-maps)의 서울 자치구 경계 GeoJSON

### 전처리

| 단계 | 내용 | 결과 |
| --- | --- | --- |
| 지역 | `근무지역`이 서울인 공고만 사용 (원본에는 경기·인천 공고가 많이 섞여 있음) | 29,439건 제외 |
| 결측 | 회사명·채용제목이 없는 행 제외 | 0건 |
| 중복 | 회사명·채용제목·자치구·마감일이 같은 공고 제외 | 82건 제외 |
| 최종 | | **10,231건** |

- 직종: `직종코드` 앞 두 자리로 한국고용직업분류(KECO) 중분류(예: 55 → 돌봄 서비스직)를 붙여 필터에 사용. 직종명 뒤의 `(550102)` 코드 표기는 제거
- 고용형태: 정규직(기간의 정함이 없는 근로계약), 시간제(같은 계약의 시간(선택)제), 계약직(기간의 정함이 있는 근로계약)으로 분류
- 마감일자: `채용시까지  26-11-15` → `2026-11-15 (채용시까지)`
- 원본 파일에 깨진 글자가 26개 있어, 그 글자만 대체 문자로 바꾸고 읽음

다른 버전의 CSV를 쓰려면 `data/jobs.csv`를 교체하거나 대시보드 사이드바에서 업로드합니다. 열 이름이 다르면 `jobdash/data_processing/columns.py`의 `COLUMN_ALIASES`에 추가합니다. `data/jobs.csv`가 없으면 샘플 데이터(`data/sample_jobs.csv`)로 실행됩니다.

## 프로젝트 구조

기능별로 폴더를 나누었습니다. `app.py`는 화면 순서만 정하고, 실제 내용은 각 폴더에 있습니다.

```
├── app.py                          # 실행 파일. 사이드바와 탭 4개를 차례로 그림
├── jobdash/
│   ├── config.py                   # 경로, 서울 25개 자치구, 선택지, 색상
│   ├── models/                     # 채용공고 데이터 모델
│   │   ├── job_posting.py          #   JobPosting
│   │   └── job_codes.py            #   직종코드 → 직종 분류 표
│   ├── data_processing/            # CSV 읽기 → 정리 → 객체 목록 관리
│   │   ├── columns.py              #   CSV 열 이름 후보
│   │   ├── csv_loader.py           #   CSVDataLoader
│   │   ├── data_cleaner.py         #   DataCleaner
│   │   └── data_manager.py         #   JobDataManager (필터·검색)
│   ├── analysis/                   # 통계 계산
│   │   ├── base.py                 #   JobAnalyzer (추상 부모)
│   │   ├── district_analyzer.py    #   DistrictAnalyzer
│   │   └── comparison_analyzer.py  #   ComparisonAnalyzer
│   └── ui/                         # Streamlit 화면
│       ├── resources.py            #   데이터·지도 캐시
│       ├── charts.py               #   공통 차트
│       ├── sidebar.py              #   데이터 선택·필터
│       └── views/                  #   탭별 화면
│           ├── overview.py         #     서울 전체 현황 (지도)
│           ├── district_detail.py  #     자치구 상세
│           ├── comparison.py       #     자치구 비교
│           └── search.py           #     채용공고 검색
├── data/                           # jobs.csv, sample_jobs.csv, 자치구 지도
├── scripts/make_sample_data.py
└── tests/                          # 폴더별 테스트 (models, data_processing, analysis)
```

## 클래스 설계

| 클래스 | 역할 | 적용 개념 |
| --- | --- | --- |
| `JobPosting` | 채용공고 1건. 신입 가능·정규직·IT 직종 여부 판정, 필터·검색어 일치 확인 | 클래스와 객체, 생성자, 클래스 변수(`required_fields`), 클래스 메서드(`from_row`), 정적 메서드(`normalize_text`), 캡슐화(읽기 전용 property) |
| `CSVDataLoader` | CSV 파일 읽기, 인코딩 자동 판별 | 단일 책임 원칙 |
| `DataCleaner` | 열 이름 맞추기, 결측치 정리, 주소에서 자치구 추출 | 정적 메서드, 단일 책임 원칙 |
| `JobDataManager` | 로더·클리너를 이용해 객체 목록 생성, 필터링, 검색 | 컴포지션, 컬렉션(list·dict·set) |
| `JobAnalyzer` | 분석기의 추상 부모 클래스. 비율·빈도 계산 공통 메서드 제공 | 추상화, 리팩토링(공통 메서드 분리) |
| `DistrictAnalyzer` | 자치구별 공고 수·모집인원, 직종·경력·고용형태·학력 분포 | 상속, 다형성(`analyze()` 재정의) |
| `ComparisonAnalyzer` | 두 지역의 신입 가능률·정규직률·대졸 이상률·IT 직종률 비교 | 상속, 다형성(`analyze()` 재정의) |

### 객체 간 상호작용

1. **데이터 로딩**: `JobDataManager.load()`가 `CSVDataLoader`로 CSV를 읽고, 각 행을 `DataCleaner.clean_row()`로 정리한 뒤 `JobPosting.from_row()`로 객체를 만들어 list에 저장
2. **필터링**: 사이드바에서 조건을 고르면 `JobDataManager.filter_jobs()`가 `JobPosting.matches_filter()`로 맞는 객체만 추출
3. **자치구 분석**: `DistrictAnalyzer(필터 결과).analyze()`가 자치구별 통계와 분포 계산
4. **지역 비교**: `ComparisonAnalyzer(기준, 비교대상).analyze()`가 네 가지 비율 계산
5. **시각화**: 분석 결과(dict)를 `ui/views/`의 각 화면이 받아 지도·막대그래프·표로 표시

## 대시보드 기능

- **서울 전체 현황**: 직종 분류·세부 직종·경력·고용형태 필터, 자치구별 공고 수(또는 모집인원)를 색 진하기로 보여주는 지도, 상위 5개 자치구
- **자치구 상세**: 지도에서 구를 클릭하거나 직접 선택하면 공고 수·모집인원·신입 가능 수와 직종 막대그래프, 경력·고용형태·학력 비율 표시
- **자치구 비교**: 선택한 구를 서울 전체 또는 다른 구와 비교하는 막대그래프와 표
- **채용공고 검색**: 회사명·채용제목·직무내용 검색, 필터·지역과 함께 적용, 공고 상세 정보 확인

## 테스트

```bash
pytest
```

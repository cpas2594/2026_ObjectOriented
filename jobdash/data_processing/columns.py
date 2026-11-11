"""CSV 열 이름 후보.

실제 CSV의 열 이름이 데이터 버전마다 조금씩 달라서, 내부 필드마다 후보를 여러 개 둔다.
앞에 있는 이름부터 찾는다. 새 CSV의 열 이름이 없으면 해당 튜플에 추가하면 된다.
"""

COLUMN_ALIASES = {
    "company": ("기업명", "기업이름", "회사명", "업체명", "CMPNY_NM"),
    "title": ("채용제목", "구인제목", "공고제목", "JO_SJ"),
    "job_type": ("모집직종", "모집직종명", "모집직종코드명", "직종", "직종명", "JOBCODE_NM"),
    "job_code": ("직종코드", "모집직종코드"),
    "career": ("경력", "경력조건코드명", "경력조건", "CAREER_CND_NM"),
    "education": ("최소학력", "학력코드명", "학력", "ACDMCR_NM"),
    "salary": ("임금조건", "급여조건", "급여", "임금", "HOPE_WAGE"),
    "employment": ("고용형태", "고용형태코드명", "EMPLYM_STLE_CMMN_MM"),
    "headcount": ("모집인원", "모집인원수", "RCRIT_NMPR_CO"),
    "deadline": ("마감일자", "접수마감일", "마감일", "RCEPT_CLOS_NM"),
    "district": ("자치구", "근무지 자치구"),
    "address": (
        "근무지역", "근무예정지", "근무예정지 주소", "근무예정지주소", "근무지주소",
        "근무지 주소", "근무지", "주소", "WORK_PARAR_BASS_ADRES_CN", "BASS_ADRES_CN",
    ),
    "description": ("직무내용", "모집요강", "DTY_CN", "GUI_LN"),
}

# 이 필드가 없으면 데이터를 쓸 수 없다
REQUIRED_COLUMNS = ("company", "title")
# 둘 중 하나는 있어야 자치구를 알 수 있다
LOCATION_COLUMNS = ("district", "address")

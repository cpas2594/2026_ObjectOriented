"""실제 데이터가 없어도 대시보드를 돌려볼 수 있도록 가짜 채용 CSV를 만든다.

    python scripts/make_sample_data.py

결과: data/sample_jobs.csv. 열 구성은 실제 서울시 CSV와 같다. (중복·결측·서울 외 주소를 일부러 섞어 정제 기능도 확인 가능)
"""
import csv
import random
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "sample_jobs.csv"

DISTRICT_WEIGHTS = {
    "강남구": 18, "서초구": 11, "영등포구": 10, "송파구": 9, "마포구": 8, "중구": 8,
    "금천구": 7, "구로구": 7, "종로구": 6, "성동구": 5, "강서구": 5, "용산구": 4,
    "동대문구": 4, "광진구": 3, "양천구": 3, "성북구": 3, "관악구": 3, "동작구": 3,
    "서대문구": 3, "노원구": 2, "은평구": 2, "강동구": 3, "중랑구": 2, "강북구": 1, "도봉구": 1,
}
# 실제 데이터처럼 '직종명(6자리 코드)' 형식
JOB_TYPES = {
    "재가 요양보호사(550102)": 25, "요양보호사(550100)": 10, "건물 청소원(561100)": 10,
    "총무 및 일반 사무원(026501)": 7, "사회복지사(231100)": 5, "간호조무사(307500)": 5,
    "단체급식 조리사(531800)": 5, "아파트·빌라 경비원(542001)": 4, "배송·납품 운전원(624102)": 4,
    "응용 소프트웨어 개발자(133200)": 2, "웹 디자이너(415501)": 2, "온라인 쇼핑 판매원(615400)": 3,
    "기타 제조 관련 단순 종사원(890000)": 5,
}
CAREERS = {"신입": 7, "경력": 20, "관계없음": 73}
EDUCATION = {"학력무관": 90, "고졸": 5, "대졸(2~3년)": 3, "대졸(4년)": 2}
EMPLOYMENT = {
    "기간의 정함이 없는 근로계약/ 파견근로 비희망/ 대체인력채용 비희망": 30,
    "기간의 정함이 없는 근로계약(시간(선택)제)/ 파견근로 비희망/ 대체인력채용 비희망": 37,
    "기간의 정함이 있는 근로계약12 개월/ 파견근로 비희망/ 대체인력채용 비희망": 33,
}
COMPANY_PREFIX = ["한빛", "누리", "다온", "새솔", "온결", "미르", "가람", "하늘", "보람", "슬기"]
COMPANY_SUFFIX = ["테크", "소프트", "물산", "케어", "푸드", "산업", "솔루션", "컨설팅", "의료재단", "유통"]
ROADS = ["테헤란로", "세종대로", "디지털로", "올림픽로", "월드컵북로", "을지로", "강남대로", "여의대로"]


def pick(weights: dict) -> str:
    return random.choices(list(weights), weights=list(weights.values()))[0]


def make_row(i: int) -> dict:
    district = pick(DISTRICT_WEIGHTS)
    job_type = pick(JOB_TYPES)
    company = f"(주){random.choice(COMPANY_PREFIX)}{random.choice(COMPANY_SUFFIX)}"
    pay = random.choice(["시급10,320원 이상,", "월급2,156,880원 이상,", "연봉30,000,000원 이상,"])
    name = job_type.rsplit("(", 1)[0]
    deadline = f"26-{random.randint(11, 12):02d}-{random.randint(1, 28):02d}"
    return {
        "기업명": company,
        "채용제목": f"{name} 채용합니다",
        "경력": pick(CAREERS),
        "마감일자": random.choice(["", "채용시까지  "]) + deadline,
        "근무지역": f"서울 {district}",
        "최소학력": pick(EDUCATION),
        "모집직종": job_type,
        "직무내용": f"{name} 업무 전반",
        "고용형태": pick(EMPLOYMENT),
        "모집인원": str(random.choice([1, 1, 1, 1, 2, 2, 3, 5])),
        "임금조건": pay,
        "근무예정지": f"서울특별시 {district} {random.choice(ROADS)} {random.randint(1, 300)}",
        "직종코드": job_type[-7:-1],
    }


def main(n: int = 1500) -> None:
    rows = [make_row(i) for i in range(n)]
    # 정제 기능 확인용 노이즈
    rows += random.sample(rows, 40)                       # 중복 40건
    for r in random.sample(rows, 15):                     # 회사명 결측 15건
        r["기업명"] = ""
    for r in random.sample(rows, 20):                     # 서울 외 지역 20건
        r["근무지역"] = "경기 성남시 분당구"
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{OUT} 에 {len(rows)}행 저장")


if __name__ == "__main__":
    main()

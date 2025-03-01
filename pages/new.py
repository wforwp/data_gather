import streamlit as st
import pandas as pd
import os
import copy  # 기존 상태를 안전하게 복사하기 위해 추가

# 데이터 저장 경로 설정
DATA_FILE = 'data.csv'
os.makedirs("form_definitions", exist_ok=True)

st.title("신규 생성 페이지")

# 요청번호 자동 생성 (YY-XX 형식)
def generate_request_number():
    year = pd.Timestamp.today().year % 100  # 연도의 끝 두 자리 (예: 2025 -> 25)
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["요청번호"] = df["요청번호"].astype(str)
        year_data = df[df["요청번호"].str.startswith(f"{year:02d}-")]
        if year_data.empty:
            return f"{year:02d}-01"
        else:
            last_number = year_data["요청번호"].str[-2:].astype(int).max() + 1
            return f"{year:02d}-{last_number:02d}"
    else:
        return f"{year:02d}-01"

request_number = generate_request_number()
st.markdown(f"**요청번호:** {request_number} (자동생성)")

# 요청자 및 요청 제목 입력
requester = st.text_input("요청자").strip()
request_title = st.text_input("요청 제목").strip()

# 항목 추가를 위한 세션 상태 초기화 (초기 상태 강제 설정)
if "fields" not in st.session_state or st.session_state.get("current_request_number") != request_number:
    st.session_state.fields = []
    st.session_state.current_request_number = request_number

# 항목 추가 버튼 클릭 시 실행될 함수 (중복 방지)
def add_field():
    new_fields = copy.deepcopy(st.session_state.fields)
    new_fields.append({
        "레이블": "",
        "데이터 타입": "문자",  # 기본값 "문자"
        "항목지정": "",        # 콤마로 구분된 옵션 입력란
        "항목지정안함": False   # 항목지정 기능 사용 여부
    })
    st.session_state.fields = new_fields

# 항목 삭제 버튼 클릭 시 실행될 함수
def remove_field(index):
    new_fields = copy.deepcopy(st.session_state.fields)
    del new_fields[index]
    st.session_state.fields = new_fields

# 항목 관리 인터페이스
st.subheader("입력 항목 정의")
field_container = st.container()

# 컬럼 구성: 레이블, 데이터 타입, 항목지정, 항목지정안함, 삭제 버튼
for idx, field in enumerate(st.session_state.fields):
    cols = field_container.columns([3, 2, 3, 2, 1])
    # 항목 레이블 입력
    with cols[0]:
        label = st.text_input(f"항목 레이블 {idx+1}", value=field["레이블"], key=f"label_{idx}")
        st.session_state.fields[idx]["레이블"] = label
    # 데이터 타입 선택 (문자, 숫자만)
    with cols[1]:
        dtype = st.selectbox(
            f"데이터 타입 {idx+1}",
            ["문자", "숫자"],
            index=["문자", "숫자"].index(field["데이터 타입"]) if field["데이터 타입"] in ["문자", "숫자"] else 0,
            key=f"type_{idx}"
        )
        st.session_state.fields[idx]["데이터 타입"] = dtype
    # 항목지정 입력란 (체크박스에 따라 비활성화)
    with cols[2]:
        spec_disabled = st.session_state.fields[idx].get("항목지정안함", False)
        spec = st.text_input(
            f"항목지정 {idx+1} (콤마로 구분)",
            value=field.get("항목지정", ""),
            key=f"spec_{idx}",
            disabled=spec_disabled
        )
        st.session_state.fields[idx]["항목지정"] = spec if not spec_disabled else ""
    # 항목지정안함 체크박스
    with cols[3]:
        nospec = st.checkbox(
            "항목지정안함",
            value=field.get("항목지정안함", False),
            key=f"nospec_{idx}"
        )
        st.session_state.fields[idx]["항목지정안함"] = nospec
        if nospec:
            st.session_state.fields[idx]["항목지정"] = ""
    # 삭제 버튼
    with cols[4]:
        if st.button("삭제", key=f"remove_{idx}"):
            remove_field(idx)

# 항목 추가 버튼
st.button("항목 추가", on_click=add_field)

# 데이터 저장 함수 (CSV에 항목지정 정보와 항목 순서를 포함)
def save_request():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["요청번호", "요청자", "요청제목", "항목", "항목지정", "값", "항목순서"])
        df.to_csv(DATA_FILE, index=False)

    df = pd.read_csv(DATA_FILE)

    # 각 항목마다 새로운 행 추가
    new_entries = []
    for order, field in enumerate(st.session_state.fields):
        if field["레이블"].strip():
            new_entries.append({
                "요청번호": request_number,
                "요청자": requester,
                "요청제목": request_title,
                "항목": field["레이블"],
                "항목지정": field["항목지정"].strip(),
                "값": "",  # 초기 입력값은 비워둠
                "항목순서": order  # 항목 순서 저장 (입력한 순서대로)
            })

    df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# 저장 및 닫기 버튼
col_save, col_cancel = st.columns(2)

with col_save:
    if st.button("저장"):
        if requester and request_title and all(f["레이블"].strip() for f in st.session_state.fields):
            save_request()
            st.success("저장되었습니다.")
            st.switch_page("main.py")
        else:
            st.warning("요청자, 요청 제목, 모든 항목 레이블을 입력해주세요.")

with col_cancel:
    if st.button("닫기"):
        st.switch_page("main.py")

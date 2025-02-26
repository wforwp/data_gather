import streamlit as st
import pandas as pd
import os

# 데이터 저장 경로 설정
DATA_FILE = 'data.csv'
os.makedirs("form_definitions", exist_ok=True)

st.title("신규 생성 페이지")

# ✅ 요청번호 자동 생성 (YY-XX 형식)
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

# ✅ 요청자 및 요청 제목 입력
requester = st.text_input("요청자").strip()
request_title = st.text_input("요청 제목").strip()

# ✅ 항목 추가를 위한 세션 상태 초기화
if 'fields' not in st.session_state or st.session_state.get('current_request_number') != request_number:
    st.session_state.fields = []
    st.session_state.current_request_number = request_number

# ✅ 항목 추가 버튼 클릭 시 실행될 함수
def add_field():
    st.session_state.fields.append({"레이블": "", "데이터 타입": "문자"})

# ✅ 항목 삭제 버튼 클릭 시 실행될 함수
def remove_field(index):
    del st.session_state.fields[index]

# ✅ 항목 관리 인터페이스
st.subheader("입력 항목 정의")
field_container = st.container()

for idx, field in enumerate(st.session_state.fields):
    cols = field_container.columns([4, 3, 2])
    with cols[0]:
        field["레이블"] = st.text_input(f"항목 레이블 {idx+1}", value=field["레이블"], key=f"label_{idx}")
    with cols[1]:
        field["데이터 타입"] = st.selectbox(f"데이터 타입 {idx+1}", ["문자", "숫자", "날짜"],
                                        index=["문자", "숫자", "날짜"].index(field["데이터 타입"]), key=f"type_{idx}")
    with cols[2]:
        if st.button("삭제", key=f"remove_{idx}"):
            remove_field(idx)
            st.experimental_rerun()

# ✅ 항목 추가 버튼
st.button("항목 추가", on_click=add_field)

# ✅ 데이터 저장 함수
def save_request():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["요청번호", "요청자", "요청제목", "항목", "값"])
        df.to_csv(DATA_FILE, index=False)

    df = pd.read_csv(DATA_FILE)

    # ✅ 요청번호별 항목을 `data.csv`에 저장 (각 항목마다 새로운 행 추가)
    new_entries = []
    for field in st.session_state.fields:
        if field["레이블"].strip():  # 공백 필터링
            new_entries.append({
                "요청번호": request_number,
                "요청자": requester,
                "요청제목": request_title,
                "항목": field["레이블"],
                "값": ""  # 초기 입력값은 비워둠
            })

    df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ✅ 저장 및 닫기 버튼
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

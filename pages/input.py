import streamlit as st
import pandas as pd
import os
import uuid  # 고유 ID 생성을 위한 라이브러리

# 데이터 파일 경로
DATA_FILE = 'data.csv'

# 선택된 요청 정보 가져오기
selected_request = st.session_state.get("selected_request")
if not selected_request:
    st.warning("선택된 요청이 없습니다.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

st.title("입력 페이지")

# 데이터 불러오기
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("데이터베이스가 존재하지 않습니다. 먼저 요청을 생성해주세요.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

# 요청번호 필터링 (해당 요청의 데이터만 사용)
df["요청번호"] = df["요청번호"].astype(str).str.strip()
selected_request_number = str(selected_request["요청번호"]).strip()
df_selected = df[df["요청번호"] == selected_request_number].copy()

# "항목" 컬럼에 값이 없는 행 제거 및 문자열로 변환
df_selected = df_selected.dropna(subset=["항목"])
df_selected["항목"] = df_selected["항목"].astype(str).str.strip()

# 각 항목마다 최초 정의된 행만 사용 (항목지정 정보도 포함)
df_unique = df_selected.drop_duplicates(subset=["항목"])
fields = df_unique[["항목", "항목지정"]].to_dict("records")

# 입력 카운터 (두 번째 입력 시 중복 방지를 위해)
if "entry_count" not in st.session_state:
    st.session_state["entry_count"] = 0

# 제출자 입력 (필수)
submitter = st.text_input("제출자 (필수)")
inputs = {}

# 각 항목별 입력 폼 생성
for field in fields:
    field_name = field["항목"]
    # CSV에서 읽어온 항목지정 값이 NaN인 경우 빈 문자열로 처리
    raw_designated = field.get("항목지정", "")
    if pd.isna(raw_designated) or str(raw_designated).strip().lower() == "nan":
        designated = ""
    else:
        designated = str(raw_designated).strip()
    
    unique_key = f"input_{submitter or 'temp'}_{field_name}_{st.session_state['entry_count']}"
    
    if designated:  # 항목지정에 값이 있으면 드롭다운 제공
        options = [opt.strip() for opt in designated.split(",") if opt.strip()]
        inputs[field_name] = st.selectbox(field_name, options, key=unique_key)
    else:
        # 항목지정안함인 경우 자유롭게 텍스트 입력 가능 (빈 값이어도 저장 가능)
        inputs[field_name] = st.text_input(field_name, key=unique_key)

# 데이터 저장 함수 (각 항목에 대해 새로운 행 추가)
def save_input_data():
    new_entries = []
    for field_name, value in inputs.items():
        new_entries.append({
            "요청번호": selected_request_number,
            "요청자": selected_request["요청자"],
            "요청제목": selected_request["요청제목"],
            "제출자": submitter or f"익명-{uuid.uuid4().hex[:4]}",
            "항목 ID": uuid.uuid4().hex[:8],
            "항목": field_name,
            "값": value
        })
    new_df = pd.DataFrame(new_entries)
    final_df = pd.concat([df, new_df], ignore_index=True)
    final_df.to_csv(DATA_FILE, index=False)
    st.session_state["entry_count"] += 1

# 저장 버튼: 제출자만 필수 입력하도록 변경
if st.button("저장"):
    if submitter:
        save_input_data()
        st.success("데이터가 저장되었습니다.")
        st.switch_page("main.py")
    else:
        st.warning("제출자 정보를 입력해주세요.")

if st.button("닫기"):
    st.switch_page("main.py")

import streamlit as st
import pandas as pd
import os
import uuid  # ✅ 고유 ID 생성을 위한 UUID 추가

# 데이터 파일 경로
DATA_FILE = 'data.csv'

# ✅ 선택된 요청 정보 가져오기
selected_request = st.session_state.get("selected_request")

if not selected_request:
    st.warning("선택된 요청이 없습니다.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

st.title("입력 페이지")

# ✅ 데이터 불러오기
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("데이터베이스가 존재하지 않습니다. 먼저 요청을 생성해주세요.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

# ✅ 요청번호 필터링 (항목 가져오기)
df["요청번호"] = df["요청번호"].astype(str).str.strip()
selected_request_number = str(selected_request["요청번호"]).strip()

df_selected = df[df["요청번호"] == selected_request_number].copy()

# ✅ "항목" 컬럼에서 NaN 제거
df_selected = df_selected.dropna(subset=["항목"])
df_selected["항목"] = df_selected["항목"].astype(str).str.strip()

# ✅ 중복 없는 고유한 항목 리스트 만들기
unique_items = df_selected["항목"].drop_duplicates().tolist()

# ✅ 입력 카운터 (두 번째 입력 시 중복 방지)
if "entry_count" not in st.session_state:
    st.session_state["entry_count"] = 0

# ✅ 입력 폼 생성 (제출자 필수 입력)
submitter = st.text_input("제출자 (필수)")
inputs = {}

if unique_items:
    for 항목 in unique_items:
        unique_key = f"input_{submitter or 'temp'}_{항목}_{st.session_state['entry_count']}"  # ✅ 고유한 key 생성
        inputs[항목] = st.text_input(f"{항목}", key=unique_key)

    # ✅ 데이터 저장 기능 (새로운 행 추가)
    def save_input_data():
        new_entries = []
        for 항목, 값 in inputs.items():
            new_entries.append({
                "요청번호": selected_request_number,
                "요청자": selected_request["요청자"],
                "요청제목": selected_request["요청제목"],
                "제출자": submitter or f"익명-{uuid.uuid4().hex[:4]}",  # ✅ 제출자가 없으면 익명 ID
                "항목 ID": uuid.uuid4().hex[:8],  # ✅ 각 항목을 구분할 수 있도록 고유 ID 부여
                "항목": 항목,
                "값": 값
            })

        new_df = pd.DataFrame(new_entries)

        # ✅ 기존 데이터와 새로운 데이터 합치기
        final_df = pd.concat([df, new_df], ignore_index=True)
        final_df.to_csv(DATA_FILE, index=False)

        # ✅ 입력 후 key 충돌 방지를 위해 카운터 증가
        st.session_state["entry_count"] += 1

    # ✅ 저장 버튼
    if st.button("저장"):
        if submitter and all(value.strip() for value in inputs.values()):
            save_input_data()
            st.success("데이터가 저장되었습니다.")
            st.switch_page("main.py")
        else:
            st.warning("모든 항목을 입력해주세요.")

else:
    st.warning(f"❌ 요청번호 {selected_request_number}에 대한 입력 항목이 없습니다. 먼저 요청을 생성해주세요.")

if st.button("닫기"):
    st.switch_page("main.py")

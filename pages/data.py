import streamlit as st
import pandas as pd
import os

# 데이터 파일 경로
DATA_FILE = 'data.csv'

# ✅ 선택된 요청 정보 가져오기
selected_request = st.session_state.get("selected_request")

if not selected_request:
    st.warning("선택된 요청이 없습니다.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

st.title("데이터 보기 페이지")

# ✅ 데이터 불러오기
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("데이터베이스가 존재하지 않습니다. 먼저 요청을 생성해주세요.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

# ✅ 요청번호 필터링 (해당 요청번호의 데이터만 표시)
df["요청번호"] = df["요청번호"].astype(str).str.strip()
selected_request_number = str(selected_request["요청번호"]).strip()

df_selected = df[df["요청번호"] == selected_request_number].copy()

# ✅ 데이터 표시
if df_selected.empty:
    st.warning(f"📌 요청번호 {selected_request_number}에 대한 데이터가 없습니다.")
else:
    st.markdown(f"""
    **📌 요청번호:** {selected_request_number}  
    **📌 요청자:** {selected_request['요청자']}  
    **📌 요청제목:** {selected_request['요청제목']}  
    """)

    st.subheader("📊 저장된 데이터")
    st.dataframe(df_selected, hide_index=True)  # ✅ 깔끔한 데이터 출력

# ✅ 닫기 버튼
if st.button("닫기"):
    st.switch_page("main.py")

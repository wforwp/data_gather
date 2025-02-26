import streamlit as st
import pandas as pd
import os

# 데이터 저장 경로 설정
DATA_FILE = 'data.csv'

# ✅ 데이터 불러오기 (파일이 없으면 예외 처리)
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("데이터베이스가 존재하지 않습니다. 먼저 요청을 생성해주세요.")
    st.stop()

st.title("메인 페이지")

# ✅ 요청번호별 한 줄만 표시 (중복 제거)
df_unique = df.drop_duplicates(subset=["요청번호"], keep="first")[["요청번호", "요청자", "요청제목"]].copy()
df_unique["선택"] = False  # 기본값은 False (선택되지 않음)

# ✅ 데이터 표시
edited_data = st.data_editor(
    df_unique,
    column_config={"선택": st.column_config.CheckboxColumn()},
    disabled=["요청번호", "요청자", "요청제목"],
    hide_index=True,
)

# ✅ 버튼 레이아웃 구성
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("신규", use_container_width=True):
        st.switch_page("pages/new.py")

with col2:
    if st.button("삭제", use_container_width=True):
        if edited_data is not None and edited_data['선택'].any():
            to_delete = edited_data[edited_data['선택']]
            df = df[~df["요청번호"].isin(to_delete["요청번호"])]
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
        else:
            st.warning("삭제 대상을 선택하세요.")

with col3:
    if st.button("입력", use_container_width=True):
        if edited_data is not None and edited_data['선택'].sum() == 1:
            selected_row = edited_data[edited_data['선택']].iloc[0]
            st.session_state['selected_request'] = selected_row.to_dict()
            st.switch_page("pages/input.py")
        else:
            st.warning("입력 대상을 선택하세요.")

with col4:
    if st.button("결과", use_container_width=True):
        if edited_data is not None and edited_data['선택'].sum() == 1:
            selected_row = edited_data[edited_data['선택']].iloc[0]
            st.session_state['selected_request'] = selected_row.to_dict()
            st.switch_page("pages/results.py")
        else:
            st.warning("결과를 확인할 대상을 선택하세요.")

with col5:
    if st.button("데이터 보기", use_container_width=True):
        if edited_data is not None and edited_data['선택'].sum() == 1:
            selected_row = edited_data[edited_data['선택']].iloc[0]
            st.session_state['selected_request'] = selected_row.to_dict()
            st.switch_page("pages/data.py")
        else:
            st.warning("데이터를 확인할 대상을 선택하세요.")

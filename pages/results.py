import streamlit as st
import pandas as pd
import os
import io  # ✅ 엑셀 파일 저장을 위한 io 추가

# 데이터 파일 경로
DATA_FILE = 'data.csv'

# ✅ 선택된 요청 정보 가져오기
selected_request = st.session_state.get("selected_request")

if not selected_request:
    st.warning("선택된 요청이 없습니다.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

st.title("결과 페이지")

# ✅ 데이터 불러오기
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("데이터베이스가 존재하지 않습니다. 먼저 요청을 생성해주세요.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

# ✅ 요청번호 필터링 (해당 요청번호의 결과만 가져오기)
df["요청번호"] = df["요청번호"].astype(str).str.strip()
selected_request_number = str(selected_request["요청번호"]).strip()

df_selected = df[df["요청번호"] == selected_request_number].copy()

# ✅ "값" 컬럼에서 NaN 제거 (입력되지 않은 항목 제거)
df_selected = df_selected.dropna(subset=["값"])
df_selected["값"] = df_selected["값"].astype(str).str.strip()

if df_selected.empty:
    st.warning(f"📌 요청번호 {selected_request_number}에 대한 입력된 데이터가 없습니다.")
else:
    # ✅ 요청번호, 요청자, 요청제목 정보 표시
    st.markdown(f"""
    **요청번호:** {selected_request_number}  
    **요청자:** {selected_request['요청자']}  
    **요청제목:** {selected_request['요청제목']}  
    """)

    # ✅ 데이터 정리: 제출자별로 항목을 컬럼으로 정렬 (여러 값도 표시)
    df_pivot = df_selected.pivot_table(index="제출자", columns="항목", values="값", aggfunc=lambda x: ', '.join(map(str, x))).reset_index()

    # ✅ 깔끔하게 데이터 정렬하여 표시
    st.subheader("입력된 데이터")
    st.dataframe(df_pivot, hide_index=True)

    # ✅ 엑셀 파일 생성 및 다운로드 버튼 추가
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="결과 데이터", index=False)
        processed_data = output.getvalue()
        return processed_data

    excel_data = convert_df_to_excel(df_pivot)
    st.download_button(
        label="📥 엑셀 다운로드",
        data=excel_data,
        file_name=f"결과_{selected_request_number}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ✅ 닫기 버튼
if st.button("닫기"):
    st.switch_page("main.py")

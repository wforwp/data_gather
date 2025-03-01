import streamlit as st
import pandas as pd
import os
import io

# 데이터 파일 경로
DATA_FILE = 'data.csv'

# 선택된 요청 정보 가져오기
selected_request = st.session_state.get("selected_request")
if not selected_request:
    st.warning("선택된 요청이 없습니다.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

st.title("결과 페이지")

# 데이터 불러오기
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("데이터베이스가 존재하지 않습니다. 먼저 요청을 생성해주세요.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("main.py")
    st.stop()

# 요청번호 필터링 (해당 요청의 데이터만 가져오기)
df["요청번호"] = df["요청번호"].astype(str).str.strip()
selected_request_number = str(selected_request["요청번호"]).strip()

# 전체 데이터를 이용해 항목순서(order mapping) 생성 (빈 값이 있는 행도 포함)
df_all = df[df["요청번호"] == selected_request_number].copy()
order_df = df_all.drop_duplicates(subset=["항목"])[["항목", "항목순서"]]
order_mapping = dict(zip(order_df["항목"], order_df["항목순서"]))

# 실제 입력된 값이 있는 행만 선택하여 피벗 테이블 생성
df_selected = df[df["요청번호"] == selected_request_number].copy()
df_selected = df_selected.dropna(subset=["값"])
df_selected["값"] = df_selected["값"].astype(str).str.strip()

if df_selected.empty:
    st.warning(f"📌 요청번호 {selected_request_number}에 대한 입력된 데이터가 없습니다.")
else:
    st.markdown(f"""
    **요청번호:** {selected_request_number}  
    **요청자:** {selected_request['요청자']}  
    **요청제목:** {selected_request['요청제목']}  
    """)

    # 제출자별로 각 항목의 값을 컬럼으로 변환하는 피벗 테이블 생성
    df_pivot = df_selected.pivot_table(
        index="제출자", 
        columns="항목", 
        values="값", 
        aggfunc=lambda x: ', '.join(map(str, x))
    ).reset_index()

    # "제출자"를 제외한 항목 컬럼 재정렬 (신규 생성 시 저장된 항목순서 기준)
    data_columns = [col for col in df_pivot.columns if col != "제출자"]
    sorted_columns = sorted(data_columns, key=lambda x: order_mapping.get(x, 999))
    final_columns = ["제출자"] + sorted_columns
    df_pivot = df_pivot[final_columns]

    st.subheader("입력된 데이터")
    st.dataframe(df_pivot, hide_index=True)

    # 엑셀 파일 다운로드 기능
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

if st.button("닫기"):
    st.switch_page("main.py")

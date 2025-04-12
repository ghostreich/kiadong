import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ✅ 페이지 설정
st.set_page_config(page_title="마인크래프트 건축물 기록", layout="centered")

# CSV 파일 경로
CSV_FILE = "buildings.csv"

# CSV 초기화
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "이름", "높이", "넓이", "길이", "건축 시작 날짜", "건축 완료 날짜",
            "건축 기간", "건축 기간(상세)", "만든 사람", "링크"
        ])
        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# 데이터 불러오기 및 저장

def load_data():
    return pd.read_csv(CSV_FILE, encoding="utf-8-sig")

def save_data(df):
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# ✅ 모드 선택 및 권한 관리
st.sidebar.title("🔐 모드 선택")
mode = st.sidebar.selectbox("앱 모드", ["보기 전용", "관리자 모드"])
readonly = (mode == "보기 전용")

if not readonly:
    pw = st.sidebar.text_input("비밀번호 입력", type="password")
    if pw != "1234":
        st.sidebar.warning("비밀번호가 틀렸습니다. 보기 전용 모드로 전환됩니다.")
        readonly = True

# 타이틀
st.title("🏗️ 마인크래프트 건축물 기록")
if readonly:
    st.info("🔒 현재는 보기 전용 모드입니다. 건축물을 추가하거나 삭제할 수 없습니다.")

# 초기화 및 데이터 로드
initialize_csv()
df = load_data()

# 탭
탭 = st.radio("메뉴 선택", ["건축물 목록 보기", "건축물 추가하기", "건축물 삭제하기"], horizontal=True)

# 건축물 목록 보기
if 탭 == "건축물 목록 보기":
    st.subheader("📋 건축물 목록")

    정렬기준 = st.selectbox("정렬 기준을 선택하세요", [
        "이름", "높이", "넓이", "길이", "건축 시작 날짜", "건축 완료 날짜",
        "건축 기간", "만든 사람"
    ])
    정렬방식 = st.radio("정렬 방식", ["오름차순", "내림차순"], horizontal=True)
    오름차순 = 정렬방식 == "오름차순"

    df_sorted = df.copy()
    try:
        if 정렬기준 in ["높이", "넓이", "길이", "건축 기간"]:
            df_sorted[정렬기준] = pd.to_numeric(df_sorted[정렬기준], errors='coerce')
        df_sorted = df_sorted.sort_values(by=정렬기준, ascending=오름차순)
    except:
        st.warning("정렬에 실패했습니다.")

    if "링크" in df_sorted.columns:
        df_sorted["링크"] = df_sorted["링크"].apply(lambda x: f"[열기]({x})" if pd.notnull(x) and str(x).strip() != "" else "")

    if df_sorted.empty:
        st.info("표시할 건축물이 없습니다.")
    else:
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)

# 건축물 추가하기
elif 탭 == "건축물 추가하기":
    st.subheader("➕ 건축물 추가")

    if readonly:
        st.warning("이 모드에서는 건축물을 추가할 수 없습니다.")
    else:
        이름 = st.text_input("건축물 이름")
        높이 = st.number_input("높이 (블록 수)", min_value=1)
        넓이 = st.number_input("넓이 (블록 수)", min_value=1)
        길이 = st.number_input("길이 (블록 수)", min_value=1)
        시작날짜 = st.date_input("건축 시작 날짜", value=datetime.today())
        완료날짜 = st.date_input("건축 완료 날짜", value=datetime.today())
        건축기간 = st.text_input("건축 기간 (며칠)", disabled=True)
        건축기간상세 = st.text_input("건축 기간(상세) (예: 3일 5시간)")
        만든사람 = st.text_input("만든 사람")
        링크 = st.text_input("관련 링크 (선택 사항)")

        저장버튼 = st.button("저장하기")

        if 저장버튼:
            if 이름 and 만든사람:
                새로운행 = pd.DataFrame([[
                    이름, 높이, 넓이, 길이,
                    시작날짜.strftime('%Y-%m-%d'), 완료날짜.strftime('%Y-%m-%d'),
                    (완료날짜 - 시작날짜).days, 건축기간상세, 만든사람, 링크
                ]], columns=[
                    "이름", "높이", "넓이", "길이", "건축 시작 날짜", "건축 완료 날짜",
                    "건축 기간", "건축 기간(상세)", "만든 사람", "링크"
                ])
                df = pd.concat([df, 새로운행], ignore_index=True)
                save_data(df)
                st.success("✅ 건축물이 저장되었습니다!")
            else:
                st.warning("⚠️ 이름과 만든 사람은 반드시 입력해야 합니다.")

# 건축물 삭제하기
elif 탭 == "건축물 삭제하기":
    st.subheader("❌ 건축물 삭제")

    if readonly:
        st.warning("이 모드에서는 건축물을 삭제할 수 없습니다.")
    else:
        이름검색 = st.text_input("삭제할 건축물 이름 검색")
        삭제후보 = df[df["이름"].str.contains(이름검색, na=False)] if 이름검색 else df

        선택 = st.selectbox("삭제할 건축물을 선택하세요", 삭제후보["이름"] if not 삭제후보.empty else ["없음"])

        if 선택 != "없음":
            if st.checkbox("정말 삭제하시겠습니까?"):
                if st.button("삭제하기"):
                    df = df[df["이름"] != 선택]
                    save_data(df)
                    st.success(f"🗑️ '{선택}' 건축물이 삭제되었습니다.")


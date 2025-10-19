import streamlit as st
import pandas as pd

st.set_page_config(page_title="Aspect Lookup Tool", layout="wide")

# ===== 데이터 불러오기 (캐시 적용) =====
@st.cache_data
def load_data():
    df_aspects = pd.read_excel("Aspects.xlsx", sheet_name="Aspects")
    df_template = pd.read_excel("Aspects.xlsx", sheet_name="Template")
    return df_aspects, df_template

df_aspects, df_template = load_data()


# ===== 문자열 정규화 함수 =====
def normalize_angle(text):
    if pd.isna(text):
        return ""
    return (
        str(text)
        .replace("′", "'")
        .replace("’", "'")
        .replace("“", "'")
        .replace("”", "'")
        .replace(" ", "")
        .strip()
    )

# ===== Degree 컬럼 정규화 =====
df_aspects["Degree"] = df_aspects["Degree"].apply(normalize_angle)

# ===== UI =====
st.title("🔭 Aspect Lookup Tool")

signs = df_aspects["Sign"].dropna().unique().tolist()

with st.form("aspect_lookup_form"):
    sign = st.selectbox("별자리", signs)
    degree = st.number_input("도 (0–29)", 0, 29, 0)
    minute = st.number_input("분 (0–59)", 0, 59, 0)
    submit = st.form_submit_button("🔍 조회 (Enter)")

if submit:
    # 입력값을 동일한 포맷으로 변환
    search_str = normalize_angle(f"{degree}°{minute:02d}'")

    # ===== 조회 =====
    row = df_aspects[
        (df_aspects["Sign"] == sign)
        & (df_aspects["Degree"].str.contains(search_str, na=False))
    ]

    if not row.empty:
        row_data = row.iloc[0]

        # Template 순서에 맞춰 결과 채우기
        results = []
        for aspect_name in df_template["Aspects"]:
            if aspect_name in row_data.index:
                results.append(row_data[aspect_name])
            else:
                results.append("—")

        df_result = df_template.copy()
        df_result["Result"] = results

        st.subheader(f"🔹 {sign} {search_str} 의 Aspect 결과")
        st.dataframe(df_result, use_container_width=True)

        # ===== CSV 다운로드 =====
        csv = df_result.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="💾 결과 CSV로 저장하기",
            data=csv,
            file_name=f"Aspect_{sign}_{degree}°{minute:02d}.csv",
            mime="text/csv"
        )

    else:
        st.warning("❌ 해당 위치의 데이터가 없습니다.")

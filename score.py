import streamlit as st
import sqlite3
import pandas as pd
import os

# ── 설정 ──────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
_DB_DIR = os.path.join(_BASE, "db")
os.makedirs(_DB_DIR, exist_ok=True)          # db 폴더 없으면 자동 생성
DB_PATH = os.path.join(_DB_DIR, "scoreDB.db")

# ── DB 초기화 ──────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS score (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL,
            kor  INTEGER NOT NULL,
            eng  INTEGER NOT NULL,
            com  INTEGER NOT NULL
        )
    """)
    con.commit()
    con.close()

# ── 데이터 삽입 ────────────────────────────────────────
def insert_student(name: str, kor: int, eng: int, com: int):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO score (name, kor, eng, com) VALUES (?, ?, ?, ?)",
        (name, kor, eng, com)
    )
    con.commit()
    con.close()

def insert_many(rows: list):
    con = sqlite3.connect(DB_PATH)
    con.executemany(
        "INSERT INTO score (name, kor, eng, com) VALUES (?, ?, ?, ?)", rows
    )
    con.commit()
    con.close()

# ── 데이터 조회 ────────────────────────────────────────
def load_scores() -> pd.DataFrame:
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name, kor, eng, com FROM score ORDER BY id", con)
    con.close()
    return df

# ── 데이터 삭제 ────────────────────────────────────────
def delete_student(row_id: int):
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM score WHERE id = ?", (row_id,))
    con.commit()
    con.close()

def clear_all():
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM score")
    con.commit()
    con.close()

# ── 학점 계산 ─────────────────────────────────────────
def grade(avg: float) -> str:
    if avg >= 90: return "A"
    if avg >= 80: return "B"
    if avg >= 70: return "C"
    if avg >= 60: return "D"
    return "F"

# ── 성적표 DataFrame 생성 ─────────────────────────────
def make_report(df: pd.DataFrame) -> pd.DataFrame:
    r = df.copy()
    r["총점"] = r["kor"] + r["eng"] + r["com"]
    r["평균"] = (r["총점"] / 3).round(1)
    r["학점"] = r["평균"].apply(grade)
    r = r.rename(columns={"name": "이름", "kor": "국어", "eng": "영어", "com": "컴퓨터"})
    return r[["id", "이름", "국어", "영어", "컴퓨터", "총점", "평균", "학점"]]

# ── 셀 색상 스타일 ─────────────────────────────────────
def color_grade(val):
    colors = {"A": "#1a7f37", "B": "#0550ae", "C": "#9a6700", "D": "#cf222e", "F": "#6e40c9"}
    return f"color: {colors.get(val, 'black')}; font-weight: bold"

def color_avg(val):
    if val >= 90: return "background-color: #d1f0d1"
    if val >= 80: return "background-color: #d4e8ff"
    if val >= 70: return "background-color: #fff3cd"
    if val >= 60: return "background-color: #ffd6d6"
    return "background-color: #ede0ff"

# ══════════════════════════════════════════════════════
#  메인 앱
# ══════════════════════════════════════════════════════
def main():
    st.set_page_config(page_title="학생 성적 관리", page_icon="📚", layout="wide")
    init_db()

    # ── 사이드바 메뉴 ──────────────────────────────────
    st.sidebar.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=60)
    st.sidebar.title("학생 성적 관리 시스템")
    st.sidebar.caption("SQLite3 + Streamlit")
    st.sidebar.divider()
    menu = st.sidebar.radio(
        "메뉴 선택",
        ["📝 학생 등록 (수동)", "📂 CSV 업로드", "📊 성적 조회", "🗑️ 데이터 관리"],
    )

    # ══════════════════════════════════════════════════
    # 메뉴 1 : 수동 입력
    # ══════════════════════════════════════════════════
    if menu == "📝 학생 등록 (수동)":
        st.title("📝 학생 등록")
        st.caption("학생 이름과 각 과목 점수(0~100)를 입력한 뒤 저장 버튼을 누르세요.")

        with st.form("input_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            name = col1.text_input("이름", placeholder="홍길동")
            kor  = col2.number_input("국어 (kor)", min_value=0, max_value=100, value=0, step=1)
            eng  = col3.number_input("영어 (eng)", min_value=0, max_value=100, value=0, step=1)
            com  = col4.number_input("컴퓨터 (com)", min_value=0, max_value=100, value=0, step=1)
            submitted = st.form_submit_button("💾 저장", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("이름을 입력해 주세요.")
            else:
                insert_student(name.strip(), int(kor), int(eng), int(com))
                total = int(kor) + int(eng) + int(com)
                avg   = round(total / 3, 1)
                st.success(f"✅ **{name.strip()}** 학생이 저장되었습니다.")
                st.info(
                    f"국어 **{int(kor)}** | 영어 **{int(eng)}** | 컴퓨터 **{int(com)}** "
                    f"→ 총점 **{total}** | 평균 **{avg}** | 학점 **{grade(avg)}**"
                )

    # ══════════════════════════════════════════════════
    # 메뉴 2 : CSV 업로드
    # ══════════════════════════════════════════════════
    elif menu == "📂 CSV 업로드":
        st.title("📂 CSV 파일 업로드")

        with st.expander("📌 CSV 형식 안내", expanded=True):
            st.markdown("""
헤더 행이 반드시 포함되어야 합니다.
컬럼 순서: **name, kor, eng, com**

```
name,kor,eng,com
홍길동,85,90,78
김철수,72,68,91
이영희,95,88,100
```
""")

        uploaded = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])

        if uploaded:
            try:
                df_up = pd.read_csv(uploaded)
                df_up.columns = [c.strip().lower() for c in df_up.columns]

                required = {"name", "kor", "eng", "com"}
                missing  = required - set(df_up.columns)
                if missing:
                    st.error(f"필수 컬럼 누락: {missing}")
                    return

                df_up = df_up[["name", "kor", "eng", "com"]].dropna()
                df_up["name"] = df_up["name"].astype(str).str.strip()
                df_up["kor"]  = pd.to_numeric(df_up["kor"],  errors="coerce").fillna(0).astype(int).clip(0, 100)
                df_up["eng"]  = pd.to_numeric(df_up["eng"],  errors="coerce").fillna(0).astype(int).clip(0, 100)
                df_up["com"]  = pd.to_numeric(df_up["com"],  errors="coerce").fillna(0).astype(int).clip(0, 100)

                # 미리보기용 성적 계산
                preview = df_up.copy()
                preview["총점"] = preview["kor"] + preview["eng"] + preview["com"]
                preview["평균"] = (preview["총점"] / 3).round(1)
                preview["학점"] = preview["평균"].apply(grade)
                preview = preview.rename(columns={"name": "이름", "kor": "국어", "eng": "영어", "com": "컴퓨터"})

                st.subheader(f"📋 미리보기  ·  {len(preview)}명")
                st.dataframe(preview, use_container_width=True)

                if st.button("💾 DB에 전체 저장", type="primary", use_container_width=True):
                    rows = [tuple(r) for r in df_up[["name","kor","eng","com"]].itertuples(index=False)]
                    insert_many(rows)
                    st.success(f"✅ {len(rows)}명 저장 완료!")
                    st.balloons()

            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")

    # ══════════════════════════════════════════════════
    # 메뉴 3 : 성적 조회
    # ══════════════════════════════════════════════════
    elif menu == "📊 성적 조회":
        st.title("📊 성적 조회")

        df = load_scores()
        if df.empty:
            st.warning("저장된 학생 데이터가 없습니다. 먼저 학생을 등록해 주세요.")
            return

        report = make_report(df)

        # ── 요약 지표 ──────────────────────────────────
        total_students = len(report)
        avg_total      = report["평균"].mean()
        best_name      = report.loc[report["평균"].idxmax(), "이름"]
        grade_counts   = report["학점"].value_counts()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 전체 학생",  f"{total_students}명")
        c2.metric("📈 전체 평균",  f"{avg_total:.1f}점")
        c3.metric("🏆 최고 평균",  best_name)
        c4.metric("🅰️ A학점 인원", f"{grade_counts.get('A', 0)}명")

        st.divider()

        # ── 검색 / 필터 ────────────────────────────────
        f1, f2 = st.columns([3, 1])
        search       = f1.text_input("🔍 이름 검색", placeholder="이름 일부를 입력하세요")
        grade_filter = f2.selectbox("학점 필터", ["전체", "A", "B", "C", "D", "F"])

        filtered = report.copy()
        if search:
            filtered = filtered[filtered["이름"].str.contains(search, na=False)]
        if grade_filter != "전체":
            filtered = filtered[filtered["학점"] == grade_filter]

        # ── 성적표 ─────────────────────────────────────
        st.subheader(f"📋 성적표  ·  {len(filtered)}명")
        # pandas 2.1+ : applymap → map 으로 변경
        _s = filtered.set_index("id").style.format({"평균": "{:.1f}"})
        try:
            styled = _s.map(color_grade, subset=["학점"]).map(color_avg, subset=["평균"])
        except AttributeError:
            styled = _s.applymap(color_grade, subset=["학점"]).applymap(color_avg, subset=["평균"])
        st.dataframe(styled, use_container_width=True, height=min(400, 60 + len(filtered) * 35))

        # ── 차트 ───────────────────────────────────────
        ch1, ch2 = st.columns(2)
        with ch1:
            st.subheader("📊 학점 분포")
            gd = (
                filtered["학점"]
                .value_counts()
                .reindex(["A","B","C","D","F"], fill_value=0)
                .reset_index()
            )
            gd.columns = ["학점", "인원"]
            st.bar_chart(gd.set_index("학점"), color="#4c72b0")

        with ch2:
            st.subheader("📊 과목별 평균")
            subj = pd.DataFrame({
                "과목":  ["국어", "영어", "컴퓨터"],
                "평균점수": [
                    filtered["국어"].mean(),
                    filtered["영어"].mean(),
                    filtered["컴퓨터"].mean(),
                ]
            })
            st.bar_chart(subj.set_index("과목"), color="#2ca02c")

        # ── CSV 다운로드 ───────────────────────────────
        st.divider()
        csv_bytes = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            "⬇️ 성적표 CSV 다운로드",
            data=csv_bytes,
            file_name="성적표.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ══════════════════════════════════════════════════
    # 메뉴 4 : 데이터 관리
    # ══════════════════════════════════════════════════
    elif menu == "🗑️ 데이터 관리":
        st.title("🗑️ 데이터 관리")

        df = load_scores()
        if df.empty:
            st.info("저장된 데이터가 없습니다.")
            return

        report = make_report(df)
        st.dataframe(report.set_index("id"), use_container_width=True)
        st.caption(f"총 {len(report)}명 저장됨")

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("🔸 개별 삭제")
            id_list = df["id"].tolist()
            id_labels = {
                row["id"]: f"ID {row['id']} – {row['name']}"
                for _, row in df.iterrows()
            }
            sel_id = st.selectbox(
                "삭제할 학생 선택",
                options=id_list,
                format_func=lambda x: id_labels[x]
            )
            if st.button("🗑️ 선택 학생 삭제", use_container_width=True):
                name_del = df.loc[df["id"] == sel_id, "name"].values[0]
                delete_student(sel_id)
                st.success(f"✅ **{name_del}** (ID {sel_id}) 삭제 완료")
                st.rerun()

        with col_b:
            st.subheader("🔴 전체 삭제")
            st.warning("⚠️ 모든 학생 데이터가 삭제됩니다. 복구할 수 없습니다.")
            confirm = st.checkbox("전체 삭제를 확인합니다.")
            if st.button("🔴 전체 데이터 삭제", use_container_width=True, disabled=not confirm):
                clear_all()
                st.success("전체 데이터가 삭제되었습니다.")
                st.rerun()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
SPAO 베스트50 주차별 대시보드
- 지난 5주 데이터 기반 이번 주 예상 순위·예상 금액/수량
- 주차별 순위 변동 (1W ~ 5W)
"""
import math
import streamlit as st
import pandas as pd
from pathlib import Path

from data_loader import get_default_data_dir, load_all_weeks
from predict import predict_this_week

st.set_page_config(
    page_title="SPAO 베스트50 예측 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터 경로: 프로젝트 data 폴더 우선, 없으면 데스크톱 NOA실습0205
DATA_DIR = get_default_data_dir()
if not DATA_DIR.exists():
    st.error(f"데이터 폴더를 찾을 수 없습니다: {DATA_DIR}")
    st.stop()

try:
    week_dfs = load_all_weeks(DATA_DIR)
except Exception as e:
    st.error(f"주차별 데이터 로드 실패: {e}")
    st.stop()

if len(week_dfs) == 0:
    st.warning("주차별 파일이 없습니다. data 폴더에 1월1주차_스파오베스트50.xls 등 5개 파일을 넣어주세요.")
    st.stop()

pred_df = predict_this_week(week_dfs)

# 주차별 매출액 (스타일코드 -> [(주차번호, 매출액), ...])
weekly_amounts = {}
for w_idx, (label, df) in enumerate(week_dfs):
    week_num = w_idx + 1
    for _, r in df.iterrows():
        code = r["스타일코드"]
        weekly_amounts.setdefault(code, []).append((week_num, int(r["판매금액"])))


def fmt_num(n: int) -> str:
    """천 단위 콤마"""
    return f"{n:,}"


def fmt_amt(n: int) -> str:
    """금액 억/만 표기 보조"""
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}억"
    if n >= 10_000:
        return f"{n / 10_000:.0f}만"
    return fmt_num(n)


def cell_with_change(value: int, diff: int, is_amount: bool = False) -> str:
    """예측값(▲/▼ 변동) HTML 조각. 상승=파랑, 하락=빨강."""
    if is_amount:
        val_str = fmt_amt(value)
    else:
        val_str = fmt_num(value)
    if diff == 0:
        return f"{val_str}"
    if diff > 0:
        d = fmt_num(diff) if not is_amount else fmt_amt(diff)
        return f'{val_str} <span style="color:#1565c0;font-weight:bold;">(▲{d})</span>'
    d = fmt_num(-diff) if not is_amount else fmt_amt(-diff)
    return f'{val_str} <span style="color:#c62828;font-weight:bold;">(▼{d})</span>'


def safe_rank(v) -> str:
    """순위 값: 정수로 표시, 없으면 -"""
    if v is None:
        return "-"
    if isinstance(v, float) and math.isnan(v):
        return "-"
    try:
        return str(int(v))
    except (ValueError, TypeError):
        return "-"


# 표시용 테이블 행 (1W~5W는 정수 문자열)
table_rows = []
for _, row in pred_df.iterrows():
    qty_cell = cell_with_change(row["예측판매수량"], row["diff_qty"], is_amount=False)
    amt_cell = cell_with_change(row["예측판매금액"], row["diff_amount"], is_amount=True)
    table_rows.append({
        "순위": row["순위"],
        "스타일코드": row["스타일코드"],
        "스타일명": row["스타일명"],
        "예측판매수량": qty_cell,
        "예측판매금액": amt_cell,
        "1W": safe_rank(row.get("rank_1w")),
        "2W": safe_rank(row.get("rank_2w")),
        "3W": safe_rank(row.get("rank_3w")),
        "4W": safe_rank(row.get("rank_4w")),
        "5W": safe_rank(row.get("rank_5w")),
    })

# ---- 1. 순위 가독성: 짝수 행은 연한 배경 + 항상 진한 글씨 ----
# ---- 2. 1W~5W 순위: 정수, 가운데 정렬 (rank-col) ----
html_css = """
<style>
  .spao-table { border-collapse: collapse; width: 100%; font-size: 14px; }
  .spao-table th, .spao-table td { border: 1px solid #b0bec5; padding: 8px 10px; text-align: left; color: #1a1a1a; }
  .spao-table th { background: #1e3a5f; color: #fff; }
  .spao-table tr:nth-child(odd)  { background: #ffffff; }
  .spao-table tr:nth-child(even) { background: #e3f2fd; }
  .spao-table tr:hover { background: #bbdefb; }
  .spao-table .num { text-align: right; }
  .spao-table .rank-col { text-align: center; min-width: 42px; }
</style>
"""

# ---- UI ----
st.title("📊 SPAO 베스트50 예측 대시보드")
st.caption("지난 5주 판매 데이터 기반 이번 주 예상 순위·판매수량·판매금액 (판매 추이만 반영, 신규 입고 정보 미반영)")

st.markdown("---")
st.subheader("이번 주 예상 순위 & 주차별 순위 변동")
st.markdown("**1W** = 1주 전(직전주), **2W** = 2주 전, … **5W** = 5주 전 순위")

# 차트 표시할 스타일코드 (버튼 클릭 시 설정)
if "chart_style_code" not in st.session_state:
    st.session_state["chart_style_code"] = None

# 행 단위 렌더링: 각 행 아래에 차트가 열리면 "해당 순위와 다음 순위 사이"에 그래프 표시
st.markdown(html_css, unsafe_allow_html=True)

# 테이블 헤더
header_cols = st.columns([0.35, 0.5, 0.8, 2, 1.2, 1.2, 0.5, 0.5, 0.5, 0.5, 0.5])
with header_cols[0]:
    st.markdown("**차트**")
with header_cols[1]:
    st.markdown("**순위**")
with header_cols[2]:
    st.markdown("**스타일코드**")
with header_cols[3]:
    st.markdown("**스타일명**")
with header_cols[4]:
    st.markdown("**예측판매수량**")
with header_cols[5]:
    st.markdown("**예측판매금액**")
with header_cols[6]:
    st.markdown("<div style='text-align:center'>**1W**</div>", unsafe_allow_html=True)
with header_cols[7]:
    st.markdown("<div style='text-align:center'>**2W**</div>", unsafe_allow_html=True)
with header_cols[8]:
    st.markdown("<div style='text-align:center'>**3W**</div>", unsafe_allow_html=True)
with header_cols[9]:
    st.markdown("<div style='text-align:center'>**4W**</div>", unsafe_allow_html=True)
with header_cols[10]:
    st.markdown("<div style='text-align:center'>**5W**</div>", unsafe_allow_html=True)

for i, (pred_row, r) in enumerate(zip(pred_df.itertuples(index=False), table_rows)):
    row_style_code = pred_row.스타일코드

    # 짝수 행 배경
    if i % 2 == 1:
        st.markdown("<div style='background:#e3f2fd; margin:0 -1rem; padding: 2px 1rem; border-radius: 4px;'>", unsafe_allow_html=True)

    row_cols = st.columns([0.35, 0.5, 0.8, 2, 1.2, 1.2, 0.5, 0.5, 0.5, 0.5, 0.5])
    with row_cols[0]:
        if st.button("차트", key=f"chart_{row_style_code}_{i}"):
            st.session_state["chart_style_code"] = row_style_code
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()
    with row_cols[1]:
        st.write(r["순위"])
    with row_cols[2]:
        st.write(r["스타일코드"])
    with row_cols[3]:
        st.write(r["스타일명"])
    with row_cols[4]:
        st.markdown(r["예측판매수량"], unsafe_allow_html=True)
    with row_cols[5]:
        st.markdown(r["예측판매금액"], unsafe_allow_html=True)
    with row_cols[6]:
        st.markdown(f"<div style='text-align:center'>{r['1W']}</div>", unsafe_allow_html=True)
    with row_cols[7]:
        st.markdown(f"<div style='text-align:center'>{r['2W']}</div>", unsafe_allow_html=True)
    with row_cols[8]:
        st.markdown(f"<div style='text-align:center'>{r['3W']}</div>", unsafe_allow_html=True)
    with row_cols[9]:
        st.markdown(f"<div style='text-align:center'>{r['4W']}</div>", unsafe_allow_html=True)
    with row_cols[10]:
        st.markdown(f"<div style='text-align:center'>{r['5W']}</div>", unsafe_allow_html=True)

    if i % 2 == 1:
        st.markdown("</div>", unsafe_allow_html=True)

    # 이 행의 차트 버튼이 선택됐으면 → 이 행과 다음 행 사이에 차트 표시
    if st.session_state.get("chart_style_code") == row_style_code:
        amounts_by_week = [0] * 5
        for w, amt in weekly_amounts.get(row_style_code, []):
            if 1 <= w <= 5:
                amounts_by_week[w - 1] = amt
        chart_df = pd.DataFrame({
            "매출액(원)": amounts_by_week,
        }, index=range(1, 6))
        chart_df.index.name = "주차"
        st.caption(f"**{row_style_code}** {getattr(pred_row, '스타일명', '')} — 주차별 매출액 추이")
        st.line_chart(chart_df)
        st.markdown("---")

st.markdown("---")
st.caption("예측판매수량·예측판매금액 괄호: 직전주 대비 변동 (▲ 상승 파랑, ▼ 하락 빨강)")

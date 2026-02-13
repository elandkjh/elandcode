# -*- coding: utf-8 -*-
"""지난 5주 판매 추이 기반 이번 주 예측 (판매수량, 판매금액)"""
import numpy as np
import pandas as pd


def _predict_next(values: list, weeks: list) -> float:
    """
    주별 값 시리즈로 다음 주 예측.
    최소 1개 이상 값이 있으면 사용. 선형 추세로 1스텝 앞 예측.
    """
    if not values or not weeks:
        return float(values[-1]) if values else 0.0
    y = np.array(values, dtype=float)
    x = np.array(weeks, dtype=float)
    if len(y) == 1:
        return float(y[0])
    # 다음 주 번호 (예: 1~5 주차면 다음은 6)
    next_week = max(weeks) + 1
    try:
        coeffs = np.polyfit(x, y, min(1, len(x) - 1))
        pred = np.polyval(coeffs, next_week)
        return max(0.0, float(pred))
    except Exception:
        return float(np.mean(y))


def build_weekly_lookup(week_dfs: list[tuple[str, pd.DataFrame]]) -> dict:
    """
    week_dfs: [(주차라벨, df), ...]  (1주차 ~ 5주차 순)
    반환: {
      style_code: {
        "style_name": str,  # 최신 주차 기준
        "weeks": [1,2,3,4,5],
        "qty": [q1,q2,...],
        "amount": [a1,a2,...],
        "rank_1w": rank in 5주차,
        "rank_2w": rank in 4주차,
        ...
        "rank_5w": rank in 1주차,
      }
    }
    """
    # 5주차 = 1W(가장 최근), 1주차 = 5W(가장 오래됨)
    # week_dfs[0]=1주차, week_dfs[4]=5주차
    lookup = {}
    for w_idx, (label, df) in enumerate(week_dfs):
        week_num = w_idx + 1  # 1~5
        df = df.copy()
        df["rank"] = df["판매금액"].rank(ascending=False).astype(int)
        for _, row in df.iterrows():
            code = row["스타일코드"]
            if code not in lookup:
                lookup[code] = {
                    "style_name": row["스타일명"],
                    "weeks": [],
                    "qty": [],
                    "amount": [],
                    "rank_1w": None,
                    "rank_2w": None,
                    "rank_3w": None,
                    "rank_4w": None,
                    "rank_5w": None,
                }
            lookup[code]["weeks"].append(week_num)
            lookup[code]["qty"].append(row["판매수량"])
            lookup[code]["amount"].append(row["판매금액"])
            # 5주차 -> rank_1w, 4주차 -> rank_2w, ...
            rank_key = f"rank_{5 - w_idx}w"
            lookup[code][rank_key] = int(row["rank"])
            lookup[code]["style_name"] = row["스타일명"]  # 항상 최신 주차 이름으로 갱신
    return lookup


def predict_this_week(week_dfs: list[tuple[str, pd.DataFrame]]) -> pd.DataFrame:
    """
    지난 5주 데이터로 이번 주 예상 판매수량·판매금액을 예측하고,
    예상금액 기준 순위를 매긴 테이블을 반환.
    컬럼: 스타일코드, 스타일명, 예측판매수량, 예측판매금액, 직전주_수량, 직전주_금액,
          rank_1w ~ rank_5w, diff_qty, diff_amount
    """
    lookup = build_weekly_lookup(week_dfs)
    rows = []
    for code, info in lookup.items():
        weeks = info["weeks"]
        qty_list = info["qty"]
        amt_list = info["amount"]
        pred_qty = _predict_next(qty_list, weeks)
        pred_amt = _predict_next(amt_list, weeks)
        last_qty = qty_list[-1] if qty_list else 0
        last_amt = amt_list[-1] if amt_list else 0
        rows.append({
            "스타일코드": code,
            "스타일명": info["style_name"],
            "예측판매수량": int(round(pred_qty)),
            "예측판매금액": int(round(pred_amt)),
            "직전주_수량": last_qty,
            "직전주_금액": last_amt,
            "diff_qty": int(round(pred_qty)) - last_qty,
            "diff_amount": int(round(pred_amt)) - last_amt,
            "rank_1w": info.get("rank_1w"),
            "rank_2w": info.get("rank_2w"),
            "rank_3w": info.get("rank_3w"),
            "rank_4w": info.get("rank_4w"),
            "rank_5w": info.get("rank_5w"),
        })
    df = pd.DataFrame(rows)
    df = df.sort_values("예측판매금액", ascending=False).reset_index(drop=True)
    df["순위"] = df.index + 1
    return df

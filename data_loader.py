# -*- coding: utf-8 -*-
"""스파오 베스트50 HTML/엑셀 주차별 데이터 로더"""
import os
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


def _parse_number(s: str) -> int:
    """쉼표 제거 후 정수 변환"""
    if not s or (isinstance(s, float) and pd.isna(s)):
        return 0
    s = str(s).strip().replace(",", "")
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def load_week_from_html(filepath: str) -> pd.DataFrame:
    """
    .xls 확장자지만 HTML 형식인 스타일별매출집계 파일을 파싱합니다.
    반환: columns [번호, 스타일코드, 스타일명, 판매수량, 판매금액]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    data = []
    for table in tables:
        thead = table.find("thead")
        if not thead:
            continue
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        if "번호" not in headers or "스타일코드" not in headers:
            continue
        tbody = table.find("tbody")
        if not tbody:
            continue
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 5:
                continue
            num = tds[0].get_text(strip=True)
            style_code = tds[1].get_text(strip=True)
            style_name = tds[2].get_text(strip=True)
            qty_str = tds[3].get_text(strip=True)
            amt_str = tds[4].get_text(strip=True)
            if not style_code:
                continue
            data.append({
                "번호": _parse_number(num),
                "스타일코드": style_code,
                "스타일명": style_name,
                "판매수량": _parse_number(qty_str),
                "판매금액": _parse_number(amt_str),
            })
        if data:
            break
    return pd.DataFrame(data)


def get_default_data_dir() -> Path:
    """프로젝트 data 폴더 또는 데스크톱 NOA실습 경로"""
    base = Path(__file__).resolve().parent
    data_dir = base / "data"
    if data_dir.exists():
        files = list(data_dir.glob("*주차*스파오*.xls")) + list(data_dir.glob("*주차*스파오*.html"))
        if files:
            return data_dir
    # 데스크톱 경로 (실습 파일 위치)
    desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "NOA실습0205"
    if desktop.exists():
        return desktop
    return data_dir


def load_all_weeks(data_dir: Path = None) -> list[tuple[str, pd.DataFrame]]:
    """
    주차별 파일을 찾아 (주차라벨, DataFrame) 리스트로 반환.
    순서: 1주차(가장 오래됨) ~ 5주차(가장 최근) → 5W, 4W, 3W, 2W, 1W 에 대응.
    """
    if data_dir is None:
        data_dir = get_default_data_dir()
    data_dir = Path(data_dir)
    week_files = []
    for i in range(1, 6):
        for name in [
            f"1월{i}주차_스파오베스트50.xls",
            f"1월{i}주차_스파오베스트50.html",
        ]:
            p = data_dir / name
            if p.exists():
                week_files.append((i, p))
                break
    week_files.sort(key=lambda x: x[0])
    result = []
    for week_num, path in week_files:
        try:
            df = load_week_from_html(str(path))
            df["주차"] = week_num
            result.append((f"{week_num}주차", df))
        except Exception as e:
            raise RuntimeError(f"파일 로드 실패 {path}: {e}") from e
    return result

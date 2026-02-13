# SPAO 베스트50 예측 대시보드

지난 5주간 스타일별 매출 데이터로 **이번 주 예상 순위·예상 판매수량·예상 판매금액**을 예측하고, **주차별 순위 변동(1W~5W)**을 한 화면에서 보는 Streamlit 대시보드입니다.

## 기능

- **이번 주 예상 순위**: 5주 판매금액 추이를 선형 추세로 extrapolation 해 6주차 예상 금액을 구하고, 그 기준으로 순위 부여
- **예측판매수량 / 예측판매금액**: 직전주(5주차) 대비 변동을 괄호 안에 표시 (▲ 파랑, ▼ 빨강)
- **1W ~ 5W**: 1주 전(직전주) ~ 5주 전 당시 순위 (해당 주에 없으면 `-`)

## 데이터

- **위치**: 다음 중 하나에서 5개 주차 파일을 읽습니다.
  1. 프로젝트의 `data` 폴더  
     - `1월1주차_스파오베스트50.xls` ~ `1월5주차_스파오베스트50.xls`
  2. (data에 파일이 없으면) `내 PC > 바탕화면 > NOA실습0205` 폴더
- 파일 형식: `.xls` 확장자지만 내부는 **HTML 테이블** (스타일별매출집계: 번호, 스타일코드, 스타일명, 판매수량, 판매금액)

## 실행 방법

```bash
cd e:\Dev\VIBETEST
pip install -r requirements.txt
python -m streamlit run app.py
```

브라우저에서 **http://localhost:8501** 이 자동으로 열리지 않으면 주소를 직접 입력해 접속하면 됩니다.

## 웹 배포 (Streamlit Community Cloud)

GitHub에 소스를 올린 뒤 **Streamlit 계정(elandcode)** 으로 [Streamlit Community Cloud](https://share.streamlit.io)에서 배포하면 웹 URL로 앱을 공유할 수 있습니다.

**자세한 절차:** 프로젝트 루트의 **[DEPLOY.md](DEPLOY.md)** 를 참고하세요.

- `data` 폴더에 5개 주차 `.xls` 파일을 넣고 저장소에 포함해야 배포된 앱에서 데이터가 로드됩니다.

## 프로젝트 구조

- `app.py` - Streamlit 대시보드 (테이블·차트·스타일)
- `data_loader.py` - HTML 형식 주차별 파일 로드
- `predict.py` - 5주 추이 기반 수량/금액 예측 및 주차별 순위 매핑
- `requirements.txt` - streamlit, pandas, beautifulsoup4, lxml, numpy
- `.streamlit/config.toml` - Streamlit 설정 (배포/테마)
- `runtime.txt` - Python 버전 (Cloud 배포용)

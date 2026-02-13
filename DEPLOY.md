# SPAO 베스트50 대시보드 — 웹 배포 가이드 (Streamlit Community Cloud)

**Streamlit 계정: elandcode** 로 배포하면 `https://elandcode-xxx.streamlit.app` 형태의 URL에서 앱을 볼 수 있습니다.

---

## Git이 없을 때: GitHub 웹에서 바로 올리기 (CLI 불필요)

**CMD나 PowerShell에서 `git` 명령을 쓸 수 없다면** 아래처럼 브라우저만으로 올릴 수 있습니다.

### 1) 데이터 폴더 준비
- `e:\Dev\VIBETEST\data` 폴더가 없다면 만듭니다.
- 그 안에 5개 파일을 넣습니다: `1월1주차_스파오베스트50.xls` ~ `1월5주차_스파오베스트50.xls`  
  (바탕화면 `NOA실습0205`에서 복사해도 됩니다.)

### 2) GitHub에 저장소 만들기
1. https://github.com 로그인 후 우측 상단 **+** → **New repository** 클릭.
2. Repository name: 예) `spao-best50-dashboard`
3. **Public** 선택 → **Create repository** (README 추가 안 해도 됨).

### 3) 웹에서 파일 올리기
1. 방금 만든 저장소 페이지에서 **"uploading an existing file"** 링크를 클릭  
   (또는 **Add file** → **Upload files**).
2. 아래 파일/폴더를 **드래그 앤 드롭** 하거나 **choose your files** 로 선택해서 올립니다.
   - 올릴 대상 (프로젝트 루트 기준):
     - `app.py`
     - `data_loader.py`
     - `predict.py`
     - `requirements.txt`
     - `runtime.txt`
     - `README.md`
     - `DEPLOY.md`
     - `.gitignore`
     - `.streamlit` 폴더 (안에 `config.toml`)
     - `data` 폴더 (안에 5개 `.xls` 파일)
3. **Commit changes** 버튼으로 올리기를 완료합니다.

> **참고:** `.streamlit` 은 숨김 폴더라서 탐색기에서 안 보일 수 있습니다.  
> **방법 A:** 탐색기 주소창에 `e:\Dev\VIBETEST\.streamlit` 입력 후 들어가서 `config.toml` 을 선택해 올리거나,  
> **방법 B:** GitHub 저장소에서 **Add file** → **Create new file** → 파일명에 **`.streamlit/config.toml`** 입력 후 아래 내용 붙여넣고 Commit.
> ```toml
> [browser]
> gatherUsageStats = false
> [server]
> headless = true
> enableCORS = false
> enableXsrfProtection = true
> [theme]
> primaryColor = "#1e3a5f"
> backgroundColor = "#ffffff"
> secondaryBackgroundColor = "#f0f2f6"
> ```

### 4) Streamlit Cloud 에 배포
1. https://share.streamlit.io 접속 → **Sign in with GitHub** (elandcode 계정으로 로그인).
2. **New app** 클릭.
3. **Repository:** 방금 파일 올린 저장소 선택 (예: `elandcode/spao-best50-dashboard`).
4. **Branch:** `main`
5. **Main file path:** `app.py`
6. **Deploy** 클릭 → 완료되면 나오는 URL로 접속해 확인.

이렇게 하면 **Git CLI 없이** 웹에서 바로 배포할 수 있습니다.

---

## (선택) 나중에 Git 설치해서 쓰고 싶을 때

나중에 CMD에서 `git` 명령을 쓰려면 **Git for Windows** 를 설치하면 됩니다.

1. **다운로드:** https://git-scm.com/download/win  
   - "Click here to download" 로 64-bit 설치 파일 받기.
2. 설치 시 **"Git from the command line and also from 3rd-party software"** 옵션을 선택해 두면 CMD/PowerShell에서 `git` 사용 가능.
3. 설치가 끝나면 **새 CMD 또는 PowerShell 창**을 열고 `git --version` 입력해 보기.

설치 후에는 이 문서의 **"2. GitHub 저장소 만들기 및 푸시"** 절에 있는 명령을 그대로 사용할 수 있습니다.

---

## 1. 데이터 파일 준비 (필수)

배포된 앱이 주차별 데이터를 읽으려면 **프로젝트의 `data` 폴더**에 아래 5개 파일이 있어야 합니다.

- `1월1주차_스파오베스트50.xls`
- `1월2주차_스파오베스트50.xls`
- `1월3주차_스파오베스트50.xls`
- `1월4주차_스파오베스트50.xls`
- `1월5주차_스파오베스트50.xls`

**할 일:**  
`e:\Dev\VIBETEST\data` 폴더를 만들고, 위 5개 파일을 그대로 복사해 넣은 뒤, 이 폴더를 Git에 포함해 푸시하세요.  
(데스크톱의 `NOA실습0205` 폴더에 있다면 그곳에서 복사하면 됩니다.)

---

## 2. GitHub 저장소 만들기 및 푸시

1. **GitHub** (https://github.com) 에 로그인합니다.
2. 우측 상단 **"+** → **New repository** 를 선택합니다.
3. Repository name 예: `spao-best50-dashboard`  
   - Public 선택 후 **Create repository** 로 생성합니다.
4. 터미널(또는 PowerShell)에서 프로젝트 폴더로 이동한 뒤, 아래를 **순서대로** 실행합니다.

```powershell
cd e:\Dev\VIBETEST

# Git이 아직 초기화되지 않았다면
git init

# 원격 저장소 연결 (본인 GitHub 사용자명/저장소이름으로 수정)
git remote add origin https://github.com/elandcode/spao-best50-dashboard.git

# 모든 파일 추가 (data 폴더 포함)
git add .

# 첫 커밋
git commit -m "SPAO 베스트50 예측 대시보드 초기 배포"

# main 브랜치로 푸시
git branch -M main
git push -u origin main
```

- GitHub 사용자명이 `elandcode`가 아니면 `elandcode` 부분을 본인 아이디로 바꾸세요.
- 저장소 이름도 `spao-best50-dashboard`가 아니면 그에 맞게 수정하세요.

---

## 3. Streamlit Community Cloud 에 배포

1. 브라우저에서 **https://share.streamlit.io** (또는 **https://streamlit.io/cloud**) 로 이동합니다.
2. **Sign in with GitHub** 로 로그인합니다. (Streamlit 계정 elandcode가 GitHub와 연결된 계정으로 로그인하면 됩니다.)
3. **"New app"** 또는 **"Create app"** 를 클릭합니다.
4. 다음처럼 설정합니다.
   - **Repository:** `elandcode/spao-best50-dashboard` (방금 푸시한 저장소 선택)
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. **Deploy** 를 누르면 빌드가 시작되고, 수 분 안에 앱이 올라갑니다.
6. 완료되면 **"Your app is live"** 와 함께 URL이 표시됩니다.  
   예: `https://spao-best50-dashboard-xxxxx.streamlit.app`  
   이 주소로 접속하면 웹에서 대시보드를 볼 수 있습니다.

---

## 4. 이후 업데이트 방법

- 로컬에서 코드나 `data` 폴더 내용을 수정한 뒤, 아래처럼 커밋하고 푸시하면 Streamlit Cloud가 자동으로 다시 배포합니다.

```powershell
cd e:\Dev\VIBETEST
git add .
git commit -m "업데이트 내용 요약"
git push
```

---

## 요약 체크리스트

**Git 없이 (웹 업로드):**
- [ ] `data` 폴더에 5개 주차 `.xls` 파일 넣기
- [ ] GitHub에 새 저장소 생성 → **Upload files** 로 프로젝트 파일 + `data` + `.streamlit/config.toml` 올리기
- [ ] https://share.streamlit.io 에서 New app → 저장소/`main`/`app.py` 선택 → Deploy
- [ ] 발급된 URL로 접속해 동작 확인

**Git 설치 후 (CLI 사용):**
- [ ] `data` 폴더에 5개 파일 넣기
- [ ] GitHub에 새 저장소 생성
- [ ] `git init` → `git remote add` → `git add .` → `git commit` → `git branch -M main` → `git push`
- [ ] share.streamlit.io 에서 New app → Deploy

이 순서대로 진행하면 elandcode 계정으로 웹에 배포되어, 브라우저에서 SPAO 베스트50 대시보드를 볼 수 있습니다.

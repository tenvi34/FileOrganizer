# 파일 자동 분류 프로그램 (File Organizer)

파일명에 포함된 키워드를 기반으로 파일을 자동으로 분류하고 지정된 폴더로 이동시키는 Windows/macOS 호환 프로그램입니다. 대량의 파일을 효율적으로 정리하고 싶은 분들을 위한 필수 도구입니다.

## 주요 기능

### 📌 핵심 기능
- **🔍 키워드 기반 자동 분류**
  - 파일명에 특정 키워드가 포함되면 자동으로 지정된 폴더로 이동
  - 대소문자 구분 없이 검색
  - 여러 키워드 규칙을 동시에 적용 가능

- **📁 스마트 폴더 관리**
  - 대상 폴더가 없으면 자동으로 생성
  - 파일명 중복 시 자동으로 번호 추가 (예: file_1.txt, file_2.txt)
  - 원본 파일의 속성(수정일 등) 유지

- **💾 규칙 저장 및 관리**
  - 한 번 설정한 규칙은 JSON 파일로 저장되어 프로그램 재시작 시에도 유지
  - 규칙 추가/삭제가 간편한 GUI 인터페이스
  - 규칙별로 다른 대상 폴더 지정 가능

### 🎯 편의 기능
- **👀 미리보기 모드**
  - 실제 파일 이동 전에 어떤 파일이 어디로 이동될지 확인
  - 예상치 못한 파일 이동 방지
  - 작업 내역을 로그로 확인

- **📊 진행 상황 표시**
  - 실시간 진행률 바
  - 현재 처리 중인 파일명 표시
  - 전체 파일 수와 완료된 파일 수 표시

- **📝 로그 관리**
  - 실시간 작업 로그
  - 로그 저장 기능
  - 별도 창에서 로그 확인 가능
  - 로그 내용 클립보드 복사

- **⚙️ 유연한 옵션**
  - 하위 폴더 포함/제외 선택 가능
  - 파일 이동/복사 모드 선택
  - 실시간 작업 로그 표시

- **🖥️ 사용자 친화적 GUI**
  - 드래그 앤 드롭 없이 버튼 클릭으로 폴더 선택
  - 직관적인 규칙 관리 인터페이스
  - 실시간 작업 상태 표시

### 🆕 v2.0.0 새로운 기능

- **완전히 새로워진 UI**: 작업 흐름에 최적화된 3단 레이아웃
- **향상된 사용성**: 직관적인 탭 구조와 실시간 미리보기
- **플랫폼 네이티브 디자인**: 각 OS에 최적화된 UI 렌더링

## 🚀 빠른 시작

### Windows 사용자 (권장)
1. [Releases](https://github.com/tenvi34/FileOrganizer/releases) 페이지에서 최신 버전의 `FileOrganizer.exe`를 다운로드
2. 다운로드한 파일을 실행 (Windows Defender 경고 시 "추가 정보" → "실행" 클릭)
3. 바로 사용 가능! (별도 설치 불필요)

### macOS/Linux 사용자
```bash
# 저장소 클론
git clone https://github.com/tenvi34/FileOrganizer.git
cd FileOrganizer

# Python 3.7 이상 필요
python3 file_organizer.py
```

## 📖 사용 방법

### 1️⃣ 기본 사용법
1. **대상 폴더 선택**: "폴더 선택" 버튼을 클릭하여 정리할 폴더 지정
2. **규칙 설정**:
   - 키워드 입력: 찾고자 하는 파일명의 일부 (예: "계약서", "2025", "사진")
   - 대상 폴더 선택: 해당 키워드 파일들이 이동될 폴더
   - "규칙 추가" 버튼 클릭
3. **옵션 설정**:
   - ✅ 하위 폴더 포함: 선택한 폴더의 모든 하위 폴더까지 검색
   - ✅ 복사: 파일을 이동하지 않고 복사 (원본 유지)
4. **실행**:
   - "미리보기": 어떤 파일들이 이동될지 미리 확인
   - "파일 정리 시작": 실제 파일 이동/복사 실행

|단축키|기능|
|-------------|------|
|Ctrl/Cmd + R|새로고침|
|Ctrl/Cmd + A|전체 선택|
|Ctrl/Cmd + D|전체 해제|
|Ctrl/Cmd + Enter|작업 실행|
|F5|새로고침|

### 2️⃣ 활용 예시

#### 📄 문서 정리
- "계약서" → `D:\문서\계약서`
- "견적서" → `D:\문서\견적서`
- "보고서" → `D:\문서\보고서`

#### 📅 연도별 정리
- "2025" → `D:\자료\2025년`
- "2024" → `D:\자료\2024년`
- "2023" → `D:\자료\2023년`

#### 📸 미디어 파일 정리
- "IMG_" → `D:\사진\핸드폰사진`
- "스크린샷" → `D:\사진\스크린샷`
- "동영상" → `D:\미디어\동영상`

#### 💼 프로젝트별 정리
- "프로젝트A" → `D:\작업\프로젝트A`
- "프로젝트B" → `D:\작업\프로젝트B`
- "임시" → `D:\작업\임시파일`

### 3️⃣ 고급 팁
- **규칙 우선순위**: 먼저 추가한 규칙이 우선 적용됩니다
- **부분 일치**: "2025"를 키워드로 설정하면 "2025-01-01_보고서.pdf"도 매칭됩니다
- **안전한 작업**: 중요한 파일은 "복사" 옵션을 사용하여 원본을 보존하세요
- **규칙 백업**: `file_organizer_config.json` 파일을 백업하면 규칙을 보존할 수 있습니다
- **대량 파일 처리**: 50개 이상의 파일을 처리할 때는 별도 로그 창을 사용하세요

## ⚠️ Windows Defender 경고

프로그램 실행 시 바이러스 경고가 나타날 수 있습니다. 이는 PyInstaller로 만든 프로그램의 일반적인 오탐지입니다.

**안전한 이유:**
- 오픈소스 코드 (GitHub에서 확인 가능)
- 파일 정리 기능만 수행
- 네트워크 접속 없음

**해결 방법:**
1. "추가 정보" → "실행" 클릭
2. 또는 Windows Defender에 예외 추가

## 🛠️ 개발자를 위한 정보

### 시스템 요구사항
- Python 3.7 이상
- tkinter (Python 기본 포함)
- Windows 7/10/11 또는 macOS 10.14 이상

### 테스트 모드 실행
- 전체 테스트
```bash
python test_file_organizer.py
```

- 빠른 테스트
```bash
python test_file_organizer.py --quick
```

### 개발 환경 설정
```bash
# 저장소 클론
git clone https://github.com/tenvi34/FileOrganizer.git
cd FileOrganizer

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 모드 실행
python file_organizer.py
```

### 빌드 방법

#### Windows 실행 파일 생성
```bash
pyinstaller --onefile --windowed --noupx --name "FileOrganizer" file_organizer.py
```

#### macOS 앱 번들 생성
```bash
pyinstaller --onefile --windowed --noupx --name "FileOrganizer" --osx-bundle-identifier "com.yourname.fileorganizer" file_organizer.py
```

### GitHub Actions 자동 빌드
태그를 푸시하면 자동으로 Windows 실행 파일이 빌드되어 Release에 업로드됩니다:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🏗️ 프로젝트 구조
```bash
file_organizer/
├── main.py              # 진입점
├── src/
│   ├── core/           # 핵심 로직
│   ├── ui/             # 사용자 인터페이스
│   └── utils/          # 유틸리티
└── logs/               # 로그 파일
```

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포할 수 있습니다.

## 🐛 알려진 이슈

- Windows Defender가 처음 실행 시 경고를 표시할 수 있습니다 (정상)
- 대용량 파일 이동 시 UI가 일시적으로 멈출 수 있습니다 (백그라운드 처리 중)
- 네트워크 드라이브에서는 속도가 느릴 수 있습니다

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
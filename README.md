# 파일 자동 분류 프로그램 (File Organizer)

파일명에 포함된 키워드를 기반으로 파일을 자동으로 분류하고 지정된 폴더로 이동시키는 Windows/macOS/Linux 호환 프로그램입니다. 대량의 파일을 효율적으로 정리하고 싶은 분들을 위한 필수 도구입니다.

## 🌟 주요 기능

### 📌 핵심 기능
- **🔍 키워드 기반 자동 분류**
  - 파일명에 특정 키워드가 포함되면 자동으로 지정된 폴더로 이동
  - 다양한 매칭 옵션: 포함/정확히/시작/끝/정규식
  - 여러 키워드 규칙을 동시에 적용 가능

- **📁 스마트 폴더 관리**
  - 대상 폴더가 없으면 자동으로 생성
  - 파일명 중복 시 자동으로 번호 추가 (예: file_1.txt, file_2.txt)
  - 원본 파일의 속성(수정일 등) 유지

- **💾 규칙 저장 및 관리**
  - 한 번 설정한 규칙은 JSON 파일로 저장되어 프로그램 재시작 시에도 유지
  - 규칙 추가/삭제가 간편한 GUI 인터페이스
  - 규칙별로 다른 대상 폴더 지정 가능
  - 설정 내보내기/불러오기 기능

### 🆕 v2.1.5 새로운 기능

- **🎯 드래그 앤 드롭**: 폴더를 직접 드래그하여 추가
- **👆 파일 더블클릭**: 파일 목록에서 더블클릭으로 바로 열기
- **🔄 실시간 모니터링**: 폴더를 감시하여 새 파일 자동 정리
- **⚡ 성능 최적화**: 대용량 파일 멀티스레드 복사, 파일 정보 캐싱
- **🔍 고급 필터링**: 파일명, 확장자, 크기, 날짜별 필터

### 🎯 편의 기능
- **👀 미리보기 모드**
  - 실제 파일 이동 전에 어떤 파일이 어디로 이동될지 확인
  - 예상치 못한 파일 이동 방지
  - 작업 내역을 로그로 확인

- **📊 진행 상황 표시**
  - 실시간 진행률 바
  - 현재 처리 중인 파일명 표시
  - 전체 파일 수와 완료된 파일 수 표시
  - 대용량 파일 복사 시 상세 진행률

- **📝 로그 관리**
  - 실시간 작업 로그
  - 로그 저장 기능
  - 별도 창에서 로그 확인 가능
  - 로그 내용 클립보드 복사

- **⚙️ 고급 설정**
  - 멀티스레드 복사 옵션
  - 파일 복사 후 검증
  - 네트워크 드라이브 최적화
  - 성능 벤치마크 도구

- **🖥️ 사용자 친화적 GUI**
  - 드래그 앤 드롭 지원
  - 직관적인 3단 레이아웃
  - 파일 타입별 아이콘 표시
  - 플랫폼 네이티브 디자인

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

# Python 3.9 이상 필요
pip install -r requirements.txt
python main.py
```

## 📖 사용 방법

### 1️⃣ 기본 사용법
1. **대상 폴더 선택**: 
   - "폴더 선택" 버튼 클릭 또는
   - 폴더를 직접 드래그 앤 드롭
2. **규칙 설정**:
   - 키워드 입력: 찾고자 하는 파일명의 일부
   - 매칭 방식 선택: 포함/정확히/시작/끝/정규식
   - 대상 폴더 선택: 해당 키워드 파일들이 이동될 폴더
   - "규칙 추가" 버튼 클릭
3. **옵션 설정**:
   - ✅ 하위 폴더 포함: 선택한 폴더의 모든 하위 폴더까지 검색
   - 작업 유형: 이동/복사/삭제
4. **실행**:
   - "미리보기": 어떤 파일들이 이동될지 미리 확인
   - "작업 실행": 실제 파일 처리 시작

### 2️⃣ 자동 파일 정리
1. 작업 옵션 탭에서 "자동 파일 정리 활성화"
2. 감시할 폴더 추가 (예: 다운로드 폴더)
3. 파일 처리 대기 시간 설정
4. 새 파일이 추가되면 자동으로 정리됩니다

### 단축키

|단축키|기능|
|-------------|------|
|Ctrl/Cmd + R|새로고침|
|Ctrl/Cmd + A|전체 선택|
|Ctrl/Cmd + D|전체 해제|
|Ctrl/Cmd + Enter|작업 실행|
|Ctrl/Cmd + P|미리보기|
|Ctrl/Cmd + S|로그 저장|
|Ctrl/Cmd + L|로그 지우기|
|F5|새로고침|

### 4️⃣ 활용 예시

#### 📄 문서 정리 (템플릿 사용)
- Word 문서 (*.doc, *.docx) → `문서/Word`
- PDF 파일 (*.pdf) → `문서/PDF`
- 스프레드시트 (*.xls, *.xlsx) → `문서/Excel`

#### 📅 날짜별 정리 (정규식)
- `^\d{4}-\d{2}-\d{2}` → 날짜로 시작하는 파일
- `^\d{8}_` → YYYYMMDD 형식
- `^\d{6}_` → YYMMDD 형식

#### 🎬 미디어 파일 정리
- `*.mp4, *.avi, *.mkv` → `동영상`
- `*.jpg, *.png, *.gif` → `이미지`
- `*.mp3, *.wav, *.flac` → `음악`

#### 💼 프로젝트별 정리
- "프로젝트A" → `작업/프로젝트A`
- "프로젝트B" → `작업/프로젝트B`
- "temp", "tmp" → `임시파일`

## 🛠️ 시스템 요구사항

- **Python**: 3.9 이상
- **운영체제**: Windows 7+, macOS 10.14+, Linux
- **필수 패키지**:
  - tkinter (Python 기본 포함)
  - send2trash 1.8.3+
  - Pillow 11.0.0+ (아이콘 표시용, 선택사항)
  - tkinterdnd2 0.4.2+ (드래그 앤 드롭용, 선택사항)
  - psutil 6.1.0+ (시스템 정보용, 선택사항)

## 🏗️ 프로젝트 구조
```
file_organizer/
├── main.py                    # 진입점
├── src/
│   ├── app.py                 # 애플리케이션 클래스
│   ├── constants.py           # 상수 정의
│   ├── core/                  # 핵심 비즈니스 로직
│   │   ├── file_matcher.py    # 파일 매칭
│   │   ├── file_processor.py  # 파일 처리
│   │   └── rule_manager.py    # 규칙 관리
│   ├── ui/                    # UI 관련
│   │   ├── main_window.py     # 메인 윈도우
│   │   ├── settings_panel.py  # 설정 패널
│   │   ├── file_list_panel.py # 파일 목록 패널
│   │   ├── status_panel.py    # 상태 패널
│   │   ├── dialogs.py         # 대화상자
│   │   └── ...                # 기타 UI 컴포넌트
│   └── utils/                 # 유틸리티
│       ├── config.py          # 설정 관리
│       ├── logger.py          # 로그 관리
│       ├── validators.py      # 검증 함수
│       ├── performance.py     # 성능 최적화
│       └── benchmark.py       # 벤치마크 도구
├── test_file_organizer.py     # 테스트
├── requirements.txt           # 의존성
└── README.md                  # 문서
```

## 📦 설치 및 빌드

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
python main.py
```

### 실행 파일 빌드

#### Windows
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico --name=FileOrganizer main.py
```

#### macOS
```bash
pyinstaller --onefile --windowed --icon=assets/icon.icns --name=FileOrganizer main.py
```

#### Linux
```bash
pyinstaller --onefile --windowed --icon=assets/icon.png --name=FileOrganizer main.py
```

## 🧪 테스트

```bash
# 전체 테스트 실행
python test_file_organizer.py

# 빠른 테스트
python test_file_organizer.py --quick

# 통합 테스트만
python test_file_organizer.py --integration
```

## 🐛 알려진 이슈 및 해결방법

### Windows Defender 경고
- PyInstaller로 만든 프로그램의 일반적인 오탐지
- 해결: "추가 정보" → "실행" 클릭 또는 Windows Defender에 예외 추가

### tkinterdnd2 오류
- 증상: "invalid command name tkdnd::drop_target"
- 해결: `pip install tkinterdnd2` 재설치

### 대용량 파일 처리
- 1GB 이상 파일은 멀티스레드 복사 자동 활성화
- 네트워크 드라이브는 자동으로 최적화 적용


---
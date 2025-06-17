# 파일 자동 분류 프로그램

파일명에 포함된 키워드를 기반으로 파일을 자동으로 분류하고 지정된 폴더로 이동시키는 프로그램입니다.

## 기능

- 🔍 **키워드 기반 파일 검색**: 파일명에 특정 키워드가 포함된 파일을 자동으로 찾습니다
- 📁 **자동 폴더 정리**: 키워드별로 지정된 폴더로 파일을 이동 또는 복사합니다
- 💾 **규칙 저장**: 설정한 분류 규칙을 저장하여 재사용할 수 있습니다
- 👀 **미리보기**: 실제 작업 전에 어떤 파일들이 이동될지 확인할 수 있습니다
- 🔄 **하위 폴더 지원**: 선택한 폴더의 하위 폴더까지 검색할 수 있습니다

## 설치 방법

### Windows 사용자
1. [Releases](https://github.com/YOUR_USERNAME/YOUR_REPO/releases) 페이지에서 최신 버전의 `FileOrganizer.exe`를 다운로드합니다
2. 다운로드한 파일을 실행합니다

### 소스코드 실행
```bash
# 저장소 클론
git clone https://github.com/tenvi34/FileOrganizer.git
cd YOUR_REPO

# Python 3.7 이상 필요
python file_organizer.py
```

## 사용 방법

1. **대상 폴더 선택**: 정리하고자 하는 폴더를 선택합니다
2. **규칙 추가**:
   - 키워드: 파일명에 포함되어야 할 텍스트
   - 이동할 폴더: 해당 키워드가 포함된 파일이 이동될 폴더
3. **옵션 설정**:
   - 하위 폴더 포함: 체크하면 하위 폴더의 파일도 검색
   - 복사: 체크하면 파일을 이동하지 않고 복사
4. **미리보기**: 실제 작업 전에 결과를 미리 확인
5. **파일 정리 시작**: 설정한 규칙에 따라 파일 정리 실행

## 예시

- 키워드 "계약서" → "D:\문서\계약서" 폴더로 이동
- 키워드 "2024" → "D:\문서\2024년" 폴더로 이동
- 키워드 "사진" → "D:\이미지\사진" 폴더로 이동

## 개발

### 필요 환경
- Python 3.7+
- tkinter (Python 기본 포함)

### 빌드
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 실행 파일 생성
pyinstaller --onefile --windowed --name "FileOrganizer" file_organizer.py

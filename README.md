# 프롬프트 관리 프로그램

자주 쓰는 AI 프롬프트를 **등록·분류·검색·즐겨찾기**하고, JSON으로 저장하며 카테고리별 Markdown으로 내보내는 콘솔(메뉴 기반) 프로그램입니다. 외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.

## 실행 방법

```bash
# 1. 환경 확인 (Python 3.10 이상, Git user.name / user.email 설정 필요)
python3 --version
git --version
git config user.name && git config user.email

# 2. 저장소 받기 및 실행
git clone https://github.com/duyeop-coder/ai_native2.git
cd ai_native2
git checkout claude/festive-newton-4ao8tc
python3 main.py

# 3. 테스트
python3 -m unittest discover -s tests -t .
```

번호를 입력해 기능을 선택하고, `0`을 입력하면 저장 후 종료합니다. 데이터는 `data/prompts.json`에 저장되며 다음 실행 때 자동으로 불러옵니다(파일이 없으면 기본 프롬프트 3개로 시작).

## 기능 (메뉴)

| 번호 | 기능 | 구분 | 설명 |
|---|---|---|---|
| 1 | 프롬프트 추가 | 필수 | 제목·내용(빈 값 재입력), 카테고리 선택/직접 입력. 같은 카테고리의 같은 제목은 덮어쓰기/다른 제목/취소 선택 |
| 2 | 전체 목록 | 필수 | 번호·즐겨찾기(★)·카테고리·제목 |
| 3 | 카테고리별 조회 | 필수 | 선택한 카테고리의 프롬프트만 출력 (직접 입력한 카테고리도 자동 포함) |
| 4 | 키워드 검색 | 필수 | 제목 **또는** 내용에 포함, 대소문자 무시 |
| 5 | 상세 보기 | 필수 | 전체 내용 표시 + **조회수 1 증가** |
| 6 | 즐겨찾기 추가/해제 | 필수 | 토글 |
| 7 | 즐겨찾기 목록 | 필수 | ★ 항목만 출력 |
| 8 | 프롬프트 수정 | 보너스 2 | Enter로 건너뛰면 기존 값 유지 |
| 9 | 프롬프트 삭제 | 보너스 2 | 확인(y/N) 후 삭제 |
| 10 | 조회수 Top 목록 | 보너스 2 | 조회수 내림차순 Top 5 |
| 11 | JSON 저장 | 보너스 1 | `data/prompts.json` |
| 12 | JSON 불러오기 | 보너스 1 | 파일 내용으로 현재 목록 교체 |
| 13 | Markdown 내보내기 | 보너스 1 | `exports/<카테고리>.md` 카테고리별 파일 생성 |
| 0 | 종료 | | 자동 저장 후 종료 |

추가·상세 보기(조회수)·즐겨찾기·수정·삭제는 실행 직후 **자동 저장**됩니다.

## 코드 구조 (`main.py`)

| 함수 | 역할 |
|---|---|
| `input_non_empty`, `input_number` | **입력 검증 전담.** 빈 값(공백 포함)은 재입력, 숫자가 아니거나 범위 밖이면 안내 후 `None` 반환 → 호출부에서 메뉴로 복귀 |
| `select_prompt`, `choose_category` | 번호로 프롬프트/카테고리 선택 (화면 번호 1부터 → 인덱스 0부터 변환은 `select_prompt` 한 곳) |
| `add_prompt`, `show_list`, `show_by_category`, `search_prompt`, `show_detail`, `toggle_favorite`, `show_favorites` | 메뉴 1개 = 함수 1개 (필수 기능) |
| `find_prompts(prompts, condition)` | 조건 함수를 받아 `(전체 목록 기준 번호, 프롬프트)`를 반환. 카테고리·검색·즐겨찾기가 같은 필터를 재사용하고, 결과 번호를 상세 보기에 그대로 쓸 수 있음 |
| `find_duplicate` | 같은 카테고리 + 같은 제목(대소문자 무시) 검사 |
| `edit_prompt`, `delete_prompt`, `show_top` | 보너스 2 |
| `save_prompts`, `load_prompts`, `normalize`, `export_markdown` | 보너스 1 (`normalize`는 필드가 빠진 파일도 안전하게 읽음) |
| `main` | 메뉴 표(`menu`) 구성 → `while True` 루프 → 선택 번호의 함수 호출 |

### 데이터 구조

`prompts`는 **딕셔너리의 리스트**입니다.

```python
{"title": "블로그 초안 작성", "content": "...", "category": "글쓰기", "favorite": False, "views": 0}
```

- 리스트: 등록 순서 유지, 번호(`prompts[number - 1]`)로 바로 접근. 단점: 제목으로 찾으려면 전체 순회(O(n))가 필요하지만 이 프로그램 규모에서는 문제가 없음.
- 딕셔너리: `prompt["title"]`처럼 필드 이름으로 접근해 읽기 쉽고, 필드(`views` 등)를 추가하기 쉬움. 제목을 키로 하는 딕셔너리는 같은 제목 프롬프트가 생길 수 있어 쓰지 않음.

### 설계 요점 (인터뷰 대비)

- **`while`을 쓰는 이유**: 사용자가 `0`을 입력할 때까지 몇 번 반복할지 알 수 없어 `for`가 아닌 `while True` 사용. 종료 조건은 `"0"` 입력(`break`)이며, `Ctrl+C`/EOF도 예외 처리로 정상 종료.
- **검색 구현**: `keyword in title.lower() or keyword in content.lower()`. `or`이므로 둘 중 한 곳만 맞아도 검색됨(`and`면 둘 다 포함해야 해서 결과가 줄어듦).
- **입력 검증 위치**: 모든 입력은 `input_non_empty`/`input_number`를 거침. 검증을 한 곳에 모아 기능 함수는 "올바른 값"만 다루도록 함.
- **커밋 기준**: 기능 1개 = 브랜치 1개 = 커밋 1~2개. 문제가 생기면 해당 기능 커밋만 되돌릴 수 있고 리뷰·원인 추적이 쉬움.
- **브랜치/병합**: 기능마다 `feature/*` 브랜치에서 개발 → 실행·테스트로 동작 확인 → `--no-ff`로 병합해 "어떤 기능이 언제 들어왔는지"가 그래프에 남김 (`docs/logs/04_git_log.txt`).

### 심화 질문에 대한 설계 답변

1. **종료 후에도 데이터 유지**: 딕셔너리 리스트가 그대로 대응되는 **JSON**을 선택(`ensure_ascii=False`로 한글 보존, 사람이 읽고 수정 가능). 시작 시 로드(없으면 기본 데이터), 변경 직후와 종료 시 저장. 파일이 깨졌다면 `.bak`으로 백업해 자동 저장이 원본을 덮어쓰지 않게 함. 단일 사용자 소규모 데이터라 DB·CSV(중첩·불리언 표현이 불편)보다 JSON이 적합.
2. **같은 제목 충돌**: 규칙은 "**같은 카테고리 + 같은 제목(대소문자 무시)**이면 충돌". 추가 시 덮어쓰기/다른 제목/취소를 선택하고, 수정으로 충돌이 생기면 거부. 다른 카테고리의 같은 제목은 허용(번호로 구분). 규모가 커지면 고유 `id` 필드를 두는 것이 다음 단계.
3. **병합 충돌 해결 순서**: ① 원인 파악 — `git status`로 충돌 파일, `git diff`로 `<<<<<<<` `=======` `>>>>>>>` 구간 확인, 양쪽 변경 의도 파악 → ② 해결 — 둘 다 필요한 내용은 합치고 마커 제거(`git add`) → ③ 검증 — `python3 main.py` 실행과 `unittest`로 확인 후 병합 커밋. 이 프로젝트는 메뉴 표(`menu`)와 함수 영역에 기능을 추가할 때 같은 위치를 수정하면 충돌이 나기 쉬움.
4. **카테고리 체계 변경**: 상단 상수 `CATEGORIES`만 수정. 목록/조회는 `get_all_categories`가 데이터에 실제 있는 카테고리도 포함하므로 기존 데이터가 조회에서 사라지지 않음. 이름을 바꿀 때는 저장된 JSON의 `category` 값도 함께 변환해야 함.

## Git 작업 기록

- 기능별 브랜치: `feature/add-list`, `feature/category-search`, `feature/favorite`, `feature/persistence-export`(보너스 1), `feature/crud-views`(보너스 2), `feature/tests`, `docs/readme` → 모두 `--no-ff` 병합
- `docs/logs/`: `01_env.txt`(Python/Git 버전·사용자 정보), `02_clone.txt`(샘플 저장소 clone), `03_run.txt`(실행 로그), `04_git_log.txt`(브랜치·병합 그래프)
- 과제 평가 문서: [evaluations/sungmin-maker_native-a-1-1.md](evaluations/sungmin-maker_native-a-1-1.md) (참고 레퍼런스 `sungmin-maker/native-a-1-1` 평가)

## 평가 항목 대응

| 평가 항목 | 위치 |
|---|---|
| 1. 기능 동작 | `main.py`, `docs/logs/`, `tests/` |
| 2. 코드 구조/설계 | 위 "코드 구조", "데이터 구조" |
| 3. 핵심 기술 원리 | 위 "설계 요점" |
| 4. 심층 인터뷰 | 위 "심화 질문에 대한 설계 답변" |
| 5. 보너스 1·2 | 메뉴 8~13, `save_prompts`/`load_prompts`/`export_markdown`/`edit_prompt`/`delete_prompt`/`show_top` |

---

## (참고) 레퍼런스 평가 요약

| 대상 저장소 | 항목 1 | 항목 2 | 항목 3 | 항목 4 | 보너스 | 평가 문서 |
|---|---|---|---|---|---|---|
| [sungmin-maker/native-a-1-1](https://github.com/sungmin-maker/native-a-1-1) | PASS | PASS | PASS | PASS | 미부여 | [평가 보기](evaluations/sungmin-maker_native-a-1-1.md) |

- 항목 1: 기능 동작 검증 / 항목 2: 코드 구조 및 설계 / 항목 3: 핵심 기술 원리 적용 / 항목 4: 심층 인터뷰 / 보너스: 보너스 1·2 구현 여부

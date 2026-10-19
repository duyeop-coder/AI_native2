"""프롬프트 관리 프로그램 (콘솔 메뉴 기반)."""

import json
import os

# 카테고리 체계는 이 상수 한 곳에서만 관리한다.
CATEGORIES = ["이미지 생성", "글쓰기", "코딩", "기타"]

DATA_FILE = os.environ.get("PROMPT_DATA_FILE", os.path.join("data", "prompts.json"))
EXPORT_DIR = os.environ.get("PROMPT_EXPORT_DIR", "exports")

DEFAULT_PROMPTS = [
    {"title": "제품 홍보 이미지", "content": "미니멀한 스튜디오 배경의 스마트워치 제품 사진, 부드러운 조명",
     "category": "이미지 생성", "favorite": False, "views": 0},
    {"title": "블로그 초안 작성", "content": "다음 주제로 서론-본론-결론 구조의 블로그 글을 작성해줘: {주제}",
     "category": "글쓰기", "favorite": False, "views": 0},
    {"title": "코드 리뷰 요청", "content": "아래 Python 코드의 버그와 개선점을 항목별로 알려줘.",
     "category": "코딩", "favorite": False, "views": 0},
]


# 실행 후 자동 저장할 메뉴 번호 (추가·상세 보기[조회수]·즐겨찾기·수정·삭제)
AUTO_SAVE_KEYS = {"1", "5", "6", "8", "9"}


# ---------- 입력 도우미 (입력 검증은 모두 여기서 처리) ----------

def input_non_empty(message):
    """공백만 입력하면 안내 후 다시 묻는다."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("빈 값은 입력할 수 없습니다. 다시 입력해주세요.")


def input_number(message, min_value, max_value):
    """min~max 범위의 정수를 입력받는다. 잘못된 입력이면 안내 후 None."""
    text = input(message).strip()
    try:
        number = int(text)
    except ValueError:
        print("숫자를 입력해주세요.")
        return None
    if not min_value <= number <= max_value:
        print(f"{min_value}~{max_value} 사이의 번호를 입력해주세요.")
        return None
    return number


# ---------- 공통 출력/선택 ----------

def print_prompt_line(number, prompt):
    star = "★" if prompt["favorite"] else " "
    print(f"{number:>2}. {star} [{prompt['category']}] {prompt['title']}")


def select_prompt(prompts):
    """전체 목록 기준 번호로 프롬프트 하나를 고른다. 실패하면 None."""
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return None
    number = input_number(f"번호를 입력하세요 (1~{len(prompts)}): ", 1, len(prompts))
    if number is None:
        return None
    return prompts[number - 1]  # 화면 번호는 1부터, 인덱스는 0부터


def choose_category():
    """기존 카테고리 번호를 고르거나 '직접 입력'으로 새 카테고리를 만든다."""
    for i, name in enumerate(CATEGORIES, 1):
        print(f"  {i}. {name}")
    print(f"  {len(CATEGORIES) + 1}. 직접 입력")
    while True:
        number = input_number("카테고리 번호: ", 1, len(CATEGORIES) + 1)
        if number is None:
            continue
        if number == len(CATEGORIES) + 1:
            return input_non_empty("새 카테고리 이름: ")
        return CATEGORIES[number - 1]


# ---------- 기능: 추가 / 목록 ----------

def find_duplicate(prompts, title, category):
    """같은 카테고리에 같은 제목(대소문자 무시)이 있으면 그 프롬프트를 반환."""
    for prompt in prompts:
        if prompt["category"] == category and prompt["title"].lower() == title.lower():
            return prompt
    return None


def add_prompt(prompts):
    title = input_non_empty("제목: ")
    content = input_non_empty("내용: ")
    category = choose_category()

    duplicate = find_duplicate(prompts, title, category)
    if duplicate:
        print(f"같은 카테고리에 같은 제목이 이미 있습니다: {duplicate['title']}")
        answer = input("1) 덮어쓰기  2) 다른 제목으로 등록  3) 취소 : ").strip()
        if answer == "1":
            duplicate["content"] = content
            print("기존 프롬프트의 내용을 덮어썼습니다.")
            return
        if answer == "2":
            title = input_non_empty("새 제목: ")
        else:
            print("등록을 취소했습니다.")
            return

    prompts.append({"title": title, "content": content, "category": category,
                    "favorite": False, "views": 0})
    print(f"등록되었습니다. (번호 {len(prompts)})")


def show_list(prompts):
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    print("\n--- 전체 프롬프트 ---")
    for number, prompt in enumerate(prompts, 1):
        print_prompt_line(number, prompt)


# ---------- 기능: 카테고리 조회 / 검색 ----------

def find_prompts(prompts, condition):
    """condition(prompt)가 참인 항목을 (전체 목록 기준 번호, 프롬프트)로 반환."""
    return [(i, p) for i, p in enumerate(prompts, 1) if condition(p)]


def print_matches(matches, empty_message):
    if not matches:
        print(empty_message)
        return
    for number, prompt in matches:
        print_prompt_line(number, prompt)


def get_all_categories(prompts):
    """CATEGORIES + 데이터에 실제 존재하는 직접 입력 카테고리(중복 제거, 순서 유지)."""
    names = list(CATEGORIES)
    for prompt in prompts:
        if prompt["category"] not in names:
            names.append(prompt["category"])
    return names


def show_by_category(prompts):
    names = get_all_categories(prompts)
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    number = input_number("조회할 카테고리 번호: ", 1, len(names))
    if number is None:
        return
    target = names[number - 1]
    print(f"\n--- [{target}] ---")
    matches = find_prompts(prompts, lambda p: p["category"] == target)
    print_matches(matches, "해당 카테고리의 프롬프트가 없습니다.")


def search_prompt(prompts):
    keyword = input_non_empty("검색어: ").lower()
    # 제목 또는(or) 내용에 포함되면 검색 결과. 대소문자는 구분하지 않는다.
    matches = find_prompts(
        prompts,
        lambda p: keyword in p["title"].lower() or keyword in p["content"].lower(),
    )
    print(f"\n--- '{keyword}' 검색 결과 ---")
    print_matches(matches, "검색 결과가 없습니다.")


# ---------- 기능: 상세 보기 / 즐겨찾기 ----------

def show_detail(prompts):
    prompt = select_prompt(prompts)
    if prompt is None:
        return
    prompt["views"] += 1  # 상세 보기를 열 때마다 조회수(사용 횟수) 기록
    print(f"\n제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {'예' if prompt['favorite'] else '아니오'}")
    print(f"조회수: {prompt['views']}")
    print(f"내용: {prompt['content']}")


def toggle_favorite(prompts):
    show_list(prompts)
    prompt = select_prompt(prompts)
    if prompt is None:
        return
    prompt["favorite"] = not prompt["favorite"]
    state = "추가" if prompt["favorite"] else "해제"
    print(f"'{prompt['title']}' 즐겨찾기를 {state}했습니다.")


def show_favorites(prompts):
    print("\n--- 즐겨찾기 ---")
    matches = find_prompts(prompts, lambda p: p["favorite"])
    print_matches(matches, "즐겨찾기한 프롬프트가 없습니다.")


# ---------- 보너스 1: JSON 저장/불러오기, Markdown 내보내기 ----------

def normalize(raw):
    """파일에서 읽은 항목에 누락된 필드를 기본값으로 채워 안전한 dict로 만든다."""
    return {
        "title": str(raw["title"]),
        "content": str(raw["content"]),
        "category": str(raw.get("category", "기타")),
        "favorite": bool(raw.get("favorite", False)),
        "views": int(raw.get("views", 0)),
    }


def save_prompts(prompts, path=None):
    path = path or DATA_FILE
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)


def load_prompts(path=None):
    """JSON을 읽어 리스트로 반환. 파일이 없거나 깨졌으면 None."""
    path = path or DATA_FILE
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return [normalize(item) for item in json.load(f)]
    except (OSError, ValueError, KeyError, TypeError):
        print(f"'{path}' 파일을 읽을 수 없습니다. (형식 오류)")
        try:
            os.replace(path, path + ".bak")  # 자동 저장이 원본을 덮어쓰지 않도록 백업
            print(f"원본을 '{path}.bak'으로 보관했습니다.")
        except OSError:
            pass
        return None


def save_menu(prompts):
    save_prompts(prompts)
    print(f"{len(prompts)}개의 프롬프트를 '{DATA_FILE}'에 저장했습니다.")


def load_menu(prompts):
    loaded = load_prompts()
    if loaded is None:
        print("불러올 데이터가 없습니다.")
        return
    prompts[:] = loaded  # 같은 리스트 객체를 유지한 채 내용만 교체
    print(f"{len(prompts)}개의 프롬프트를 불러왔습니다.")


def export_markdown(prompts):
    """카테고리별로 exports/<카테고리>.md 파일을 만든다."""
    if not prompts:
        print("내보낼 프롬프트가 없습니다.")
        return
    os.makedirs(EXPORT_DIR, exist_ok=True)
    for category in get_all_categories(prompts):
        items = [p for p in prompts if p["category"] == category]
        if not items:
            continue
        lines = [f"# {category}", ""]
        for p in items:
            star = " ★" if p["favorite"] else ""
            lines += [f"## {p['title']}{star}", "", p["content"], "",
                      f"- 조회수: {p['views']}", ""]
        safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in category)
        path = os.path.join(EXPORT_DIR, f"{safe}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"{path} ({len(items)}개)")


# ---------- 메뉴 ----------

def show_menu(menu):
    print("\n===== 프롬프트 관리 =====")
    for key, label, _ in menu:
        print(f"{key}. {label}")
    print("0. 종료")


def main():
    # 저장된 파일이 있으면 불러오고, 없으면 기본 데이터로 시작한다.
    prompts = load_prompts() or [dict(p) for p in DEFAULT_PROMPTS]
    menu = [
        ("1", "프롬프트 추가", add_prompt),
        ("2", "전체 목록", show_list),
        ("3", "카테고리별 조회", show_by_category),
        ("4", "키워드 검색", search_prompt),
        ("5", "상세 보기", show_detail),
        ("6", "즐겨찾기 추가/해제", toggle_favorite),
        ("7", "즐겨찾기 목록", show_favorites),
        ("11", "JSON 저장", save_menu),
        ("12", "JSON 불러오기", load_menu),
        ("13", "카테고리별 Markdown 내보내기", export_markdown),
    ]  # end menu
    actions = {key: func for key, _, func in menu}

    while True:
        show_menu(menu)
        choice = input("메뉴 번호를 입력하세요: ").strip()
        if choice == "0":
            save_prompts(prompts)  # 종료 시 자동 저장
            print("저장 후 프로그램을 종료합니다.")
            break
        if choice in actions:
            actions[choice](prompts)
            if choice in AUTO_SAVE_KEYS:
                save_prompts(prompts)  # 데이터가 바뀌는 기능은 실행 직후 자동 저장
        else:
            print(f"잘못된 입력입니다. 메뉴 번호(0~{len(menu)})를 입력해주세요.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")

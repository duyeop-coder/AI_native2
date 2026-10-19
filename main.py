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


# ---------- 메뉴 ----------

def show_menu(menu):
    print("\n===== 프롬프트 관리 =====")
    for key, label, _ in menu:
        print(f"{key}. {label}")
    print("0. 종료")


def main():
    prompts = [dict(p) for p in DEFAULT_PROMPTS]
    menu = [
        ("1", "프롬프트 추가", add_prompt),
        ("2", "전체 목록", show_list),
    ]  # end menu
    actions = {key: func for key, _, func in menu}

    while True:
        show_menu(menu)
        choice = input("메뉴 번호를 입력하세요: ").strip()
        if choice == "0":
            print("프로그램을 종료합니다.")
            break
        if choice in actions:
            actions[choice](prompts)
        else:
            print(f"잘못된 입력입니다. 메뉴 번호(0~{len(menu)})를 입력해주세요.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")

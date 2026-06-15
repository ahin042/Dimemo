import json
import os
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

DATA_FOLDER = "data"
CURRENT_USER = "사용자"  # 기본 이름 설정


def safe_name(name):
    result = ""
    for ch in name:
        if ch.isalnum() or ch in "_-":
            result += ch
        else:
            result += "_"
    return result


def get_file_paths(name):
    user_file_name = safe_name(name)
    diary_file = os.path.join(DATA_FOLDER, f"{user_file_name}_diary.txt")
    memo_file = os.path.join(DATA_FOLDER, f"{user_file_name}_memo.txt")
    return diary_file, memo_file


def load_data(name):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    diary_file, memo_file = get_file_paths(name)
    d, m = {}, {}

    if os.path.exists(diary_file):
        with open(diary_file, "r", encoding="utf-8") as file:
            try:
                d = json.load(file)
            except json.JSONDecodeError:
                d = {}

    if os.path.exists(memo_file):
        with open(memo_file, "r", encoding="utf-8") as file:
            try:
                m = json.load(file)
            except json.JSONDecodeError:
                m = {}
    return d, m


def save_data(name, d, m):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    diary_file, memo_file = get_file_paths(name)

    with open(diary_file, "w", encoding="utf-8") as file:
        json.dump(d, file, ensure_ascii=False, indent=4)

    with open(memo_file, "w", encoding="utf-8") as file:
        json.dump(m, file, ensure_ascii=False, indent=4)


def format_date(date_str):
    if not date_str:
        return None
    parts = date_str.split("-")
    if len(parts) == 3:
        return f"{parts[0]}년{parts[1]}월{parts[2]}일"
    return date_str


@app.route("/")
def index():
    d, m = load_data(CURRENT_USER)
    # 날짜 정렬 후 메인 화면으로 전달
    sorted_d = dict(sorted(d.items(), reverse=True))
    sorted_m = dict(sorted(m.items(), reverse=True))
    return render_template(
        "index.html", name=CURRENT_USER, diaries=sorted_d, memos=sorted_m
    )


@app.route("/change_user", methods=["POST"])
def change_user():
    global CURRENT_USER
    new_name = request.form.get("name", "").strip()
    if new_name:
        CURRENT_USER = new_name
    return redirect(url_for("index"))


@app.route("/diary/add", methods=["POST"])
def diary_add():
    d, m = load_data(CURRENT_USER)
    raw_date = request.form.get("date")
    text = request.form.get("text", "").strip()

    if raw_date and text:
        date_key = format_date(raw_date)
        d[date_key] = text
        save_data(CURRENT_USER, d, m)

    return redirect(url_for("index"))


@app.route("/diary/delete/<date_key>")
def diary_delete(date_key):
    d, m = load_data(CURRENT_USER)
    if date_key in d:
        del d[date_key]
        save_data(CURRENT_USER, d, m)
    return redirect(url_for("index"))


@app.route("/memo/add", methods=["POST"])
def memo_add():
    d, m = load_data(CURRENT_USER)
    raw_date = request.form.get("date")
    text = request.form.get("text", "").strip()

    if raw_date and text:
        date_key = format_date(raw_date)
        if date_key not in m:
            m[date_key] = []
        m[date_key].append(text)
        save_data(CURRENT_USER, d, m)

    return redirect(url_for("index"))


@app.route("/memo/delete/<date_key>/<int:index>")
def memo_delete(date_key, index):
    d, m = load_data(CURRENT_USER)
    if date_key in m:
        try:
            m[date_key].pop(index)
            if len(m[date_key]) == 0:
                del m[date_key]
            save_data(CURRENT_USER, d, m)
        except IndexError:
            pass
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
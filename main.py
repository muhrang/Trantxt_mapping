import re
import pandas as pd
from tkinter import Tk, filedialog

# --------------------------------------------------------------------------------
# 1. TXT 파일 선택 & 읽기
# --------------------------------------------------------------------------------
def load_txt_file():
    Tk().withdraw()  # Tk 창 숨김
    file_path = filedialog.askopenfilename(
        title="result.txt 선택",
        filetypes=[("Text Files", "*.txt")]
    )
    if not file_path:
        raise RuntimeError("❌ 파일이 선택되지 않았습니다.")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read(), file_path


# --------------------------------------------------------------------------------
# 2. 데이터 파싱
# --------------------------------------------------------------------------------
def parse_raw_text(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    parsed_data = []

    i = 0
    while i < len(lines):
        cur = lines[i]

        if i + 1 < len(lines) and re.match(r'^-?\d+(\.\d+)?$', lines[i + 1]):
            parsed_data.append({
                "type": "STOCK",
                "name": cur,
                "value": float(lines[i + 1])
            })
            i += 2
        else:
            parsed_data.append({
                "type": "THEME",
                "name": cur,
                "value": None
            })
            i += 1

    return parsed_data


# --------------------------------------------------------------------------------
# 3. Reversal Rule 로직
# --------------------------------------------------------------------------------
def organize_columns(data):
    columns = [[], [], [], []]
    closed = [False] * 4
    last_vals = [float('inf')] * 4
    theme_reset = [False] * 4
    col = 0

    for item in data:
        placed = False

        while not placed:
            if closed[col]:
                col = (col + 1) % 4
                continue

            # 테마
            if item["type"] == "THEME":
                columns[col].append(item["name"])
                theme_reset[col] = True
                placed = True

            # 종목
            else:
                v = item["value"]

                if theme_reset[col]:
                    columns[col].append(f"{item['name']} ({v})")
                    last_vals[col] = v
                    theme_reset[col] = False
                    placed = True

                else:
                    if v <= last_vals[col]:
                        columns[col].append(f"{item['name']} ({v})")
                        last_vals[col] = v
                        placed = True
                    else:
                        print(
                            f"🚫 [역전] {col+1}열 폐쇄 → "
                            f"{item['name']}({v}) > {last_vals[col]}"
                        )
                        closed[col] = True

            if placed:
                col = (col + 1) % 4

    return columns


# --------------------------------------------------------------------------------
# 4. 실행
# --------------------------------------------------------------------------------
raw_text, file_path = load_txt_file()
print(f"📂 불러온 파일: {file_path}")

parsed = parse_raw_text(raw_text)
print(f"✅ 파싱 완료: {len(parsed)}개 항목")

cols = organize_columns(parsed)

# 길이 맞춤
max_len = max(len(c) for c in cols)
for c in cols:
    c.extend([""] * (max_len - len(c)))

df = pd.DataFrame({
    "1열": cols[0],
    "2열": cols[1],
    "3열": cols[2],
    "4열": cols[3],
})

print("\n✅ 최종 결과")
print(df.to_string())

df.to_csv("final_sorted_result.csv", index=False, encoding="utf-8-sig")
print("\n💾 final_sorted_result.csv 저장 완료")

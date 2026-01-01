import re
import pandas as pd

# --------------------------------------------------------------------------------
# 1. 입력 데이터 (사용자님의 result.txt 내용)
# --------------------------------------------------------------------------------
raw_text = """
반도체
자동차
바이오
우주
제이엔비
29.96
성문전자
29.97
원익
29.9
비츠로넥스텍
13.70
제주반도체
19.69
성문전자무
29.86
아미노로직스
29.9
이노스페이스
8.72
에스에이엠티
13.39
삼보모터스
22.99
더블유에스마이
16.2
쎄트렉아이
8.15
저스템
11.30
비나텍
8.61
유틸렉스
14.8
스피어
7.38
아이언디바이스
11.07
현대오토에버
5.61
리브스메드
11.7
나노팀
3.77
네오셈
9.79
철도
메디아나
11.6
세아베스틸지주
2.57
켐트로스
9.08
율촌
29.95
지니너스
10.0
아주IB투자
-0.69
에이엘티
8.84
남북경협
강스템바이오텍
8.6
에이치브이엠
-0.84
어보브반도체
7.09
형지엘리트
13.43
코리아써우
8.5
켄코마에어로스페이스
-1.59
SK스퀘어
6.65
녹십자
6.56
노타
7.0
한국항공우주
-2.72
건설
CG인바이츠
6.9
쎄크
-7.96
상지건설
19.28
코마스템켐온
6.8
스마트폰
태영건설무
13.83
인벤티지랩
1.3
키네마스터
30.00
일성건설
11.78
삼성에피스홀딩스
0.5
옵티코어
14.91
동부건설무
11.59
올릭스
0.2
엑스플러스
10.87
동신건설
8.95
종근당
-0.4
코리아써키트
10.65
프로티나
-1.0
해성옵틱스
6.83
리가켐바이오
-1.2
"""

# --------------------------------------------------------------------------------
# 2. 데이터 파싱 (Parsing Logic)
# 텍스트를 읽어 [이름, 등락률] 쌍으로 변환합니다.
# --------------------------------------------------------------------------------
def parse_raw_text(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    parsed_data = []
    
    i = 0
    while i < len(lines):
        current_item = lines[i]
        
        # 현재 항목이 텍스트이고, 다음 항목이 숫자(등락률)인 경우 -> [종목]
        if i + 1 < len(lines) and re.match(r'^-?\d+(\.\d+)?$', lines[i+1]):
            name = current_item
            value = float(lines[i+1])
            parsed_data.append({'type': 'STOCK', 'name': name, 'value': value})
            i += 2 # 이름과 숫자를 모두 썼으므로 2칸 점프
            
        # 다음 항목이 숫자가 아니거나 없을 경우 -> [테마명]
        else:
            parsed_data.append({'type': 'THEME', 'name': current_item, 'value': None})
            i += 1
            
    return parsed_data

# --------------------------------------------------------------------------------
# 3. 핵심 알고리즘 (The "Reversal Rule" Logic)
# --------------------------------------------------------------------------------
def organize_columns(data):
    # 4개의 빈 기둥 생성
    columns = [[], [], [], []]
    
    # 상태 변수들
    current_col_idx = 0           # 현재 0~3열 중 어디를 가리키는가
    closed_flags = [False] * 4    # 열 폐쇄 여부 (True면 폐쇄)
    last_values = [float('inf')] * 4 # 각 열의 마지막 등락률 (초기값: 무한대)
    theme_reset = [False] * 4     # 테마명 등장 직후인가? (역전 판단 유예 플래그)

    for item in data:
        placed = False
        
        # 데이터를 배치할 때까지 반복 (폐쇄된 열은 건너뜀)
        while not placed:
            
            # 1. 현재 열이 폐쇄되었는지 확인 -> 폐쇄됐다면 다음 열로 이동
            if closed_flags[current_col_idx]:
                current_col_idx = (current_col_idx + 1) % 4
                continue

            # 2. 배치 로직 시작
            # -------------------------------------------------
            # CASE A: 테마명인 경우 (무조건 배치, 리셋 발동)
            # -------------------------------------------------
            if item['type'] == 'THEME':
                columns[current_col_idx].append(item['name']) # 이름만 넣음
                theme_reset[current_col_idx] = True           # ★ 리셋 플래그 ON
                placed = True # 배치 성공
                
            # -------------------------------------------------
            # CASE B: 종목(숫자 포함)인 경우 (역전 체크)
            # -------------------------------------------------
            else:
                current_val = item['value']
                last_val = last_values[current_col_idx]
                is_reset = theme_reset[current_col_idx]
                
                # 규칙 1: 테마 리셋 상태면 -> 묻지도 따지지도 않고 안착
                if is_reset:
                    columns[current_col_idx].append(f"{item['name']} ({current_val})")
                    last_values[current_col_idx] = current_val # 기준값 갱신
                    theme_reset[current_col_idx] = False       # 리셋 사용했으니 OFF
                    placed = True
                    
                # 규칙 2: 리셋 아님 -> 등락률 비교
                else:
                    # 정상 하락 (현재값 <= 이전값)
                    if current_val <= last_val:
                        columns[current_col_idx].append(f"{item['name']} ({current_val})")
                        last_values[current_col_idx] = current_val
                        placed = True
                        
                    # ★ 역전 발생 (현재값 > 이전값) -> 열 폐쇄!
                    else:
                        print(f"🚫 [역전 감지] {current_col_idx+1}열 폐쇄! 원인: {item['name']}({current_val}) > 이전값({last_val})")
                        closed_flags[current_col_idx] = True # 영구 폐쇄
                        # placed = False 상태로 유지되므로, while 루프가 돌면서 다음 열을 찾게 됨
            
            # 3. 배치가 성공했다면 -> 다음 데이터를 위해 열 인덱스 1칸 이동
            if placed:
                current_col_idx = (current_col_idx + 1) % 4
                
    return columns

# --------------------------------------------------------------------------------
# 4. 실행 및 저장
# --------------------------------------------------------------------------------
# 1) 파싱
parsed_data = parse_raw_text(raw_text)
print(f"✅ 데이터 파싱 완료: 총 {len(parsed_data)}개 항목\n")

# 2) 로직 수행
final_columns = organize_columns(parsed_data)

# 3) 결과 정리 (데이터 프레임 변환을 위해 길이 맞춤)
max_len = max(len(col) for col in final_columns)
for col in final_columns:
    while len(col) < max_len:
        col.append("") # 빈칸 채우기

df = pd.DataFrame({
    '1열 (반도체/건설)': final_columns[0],
    '2열 (자동차/철도)': final_columns[1],
    '3열 (바이오)': final_columns[2],
    '4열 (우주/스마트폰)': final_columns[3]
})

print("\n✅ 최종 변환 결과:")
print(df.to_string())

# 4) 파일 저장
df.to_csv("final_sorted_result.csv", index=False, encoding='utf-8-sig')
print("\n💾 'final_sorted_result.csv' 파일로 저장되었습니다.")

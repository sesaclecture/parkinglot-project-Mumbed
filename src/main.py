""" 
주차 관리 시스템
"""
from enum import Enum
import datetime
import random
import json



class Action(Enum):
    ENTER = "1.입차"
    LEAVE = "2.출차"
    EXIT = "3.시스템 종료"


class ParkingImage(Enum):
    ABLE = "🅿️"
    DISABLE = "🚗"

# 주차번호 0~99 or 1~100
# parking number = row * 10 + column


class ParkingSpec(Enum):
    FLOOR = 3
    ROW = 10
    # column
    COL = 10


# 현재 차량 정보 DB
# 차량번호: car_num0
# user_db = {
#     # example
#     "car_num0": {
#         # yyyy-mm-dd HH:MM
#         "start_time": "2023-01-01 10:00",
#         "end_time": "",
#         "is_guest": False,
#         "floor": 1,
#         # 0 < position_num and position_num < row x col
#         "position_num": 2,
#     },
#     # ...
# }

# # 출차시 추가
# user_history_db = {
#     # example
#     "car_num0": [
#         {
#             "start_time": "2023-01-01 10:00",
#             "end_time": "2023-01-01 12:00",
#             "is_guest": False,
#             "floor": 1,
#             "position_num": 2,
#             "payment": 3500,
#         },
#         {
#             "start_time": "2023-01-02 14:00",
#             "end_time": "2023-01-02 16:00",
#             "is_guest": False,
#             "floor": 2,
#             "position_num": 1,
#             "payment": 6000,
#         },
#         # , ...
#     ],
#     "car_num1": [
#         {
#             "start_time": "2023-01-03 09:00",
#             "end_time": "2023-01-03 11:30",
#             "is_guest": True,
#             "floor": 1,
#             "position_num": 5,
#             "payment": 8000,
#         }
#     ],
#     # ...
# }


# 3차원 배열 [floor][row][col]
parking_state = []
user_db = {}
user_history_db = {}


def init_parking_state():
    """
      주차 상태 초기화
      dummy data
    """
    global parking_state, user_db, user_history_db
    parking_state = [
        [
            [
                ParkingImage.ABLE for _ in range(ParkingSpec.COL.value)
            ]
            for _ in range(ParkingSpec.ROW.value)
        ]
        for _ in range(ParkingSpec.FLOOR.value)
    ]

    # 전체 주차 공간 개수
    total_spots = ParkingSpec.FLOOR.value * ParkingSpec.ROW.value * ParkingSpec.COL.value

    # 30% 미만의 자리만 DISABLE로 설정 << 변경 가능
    disable_count = int(total_spots * 0.3)

    all_positions = [
        (f, r, c)
        for f in range(ParkingSpec.FLOOR.value)
        for r in range(ParkingSpec.ROW.value)
        for c in range(ParkingSpec.COL.value)
    ]
    # print(all_positions)

    # 랜덤하게 disable_count만큼 선택
    disable_positions = random.sample(all_positions, disable_count)

    user_db.clear()
    user_history_db.clear()

    # disable된 자리마다 차량 정보 생성 (현재 주차중, end_time="")
    for idx, (f, r, c) in enumerate(disable_positions):
        parking_state[f][r][c] = ParkingImage.DISABLE
        car_number = f"car_num{idx}"
        # use datetime

        user_db[car_number] = {
            "start_time": (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1,10))).strftime("%Y-%m-%d %H:%M"),
            "end_time": "",
            "is_guest": False,
            "floor": f + 1,
            "position_num": r * ParkingSpec.COL.value + c + 1,
        }
        if idx % 2 == 0:
            user_history_db[car_number] = []
            days_ago = random.randint(1, 5)
            user_history_db[car_number].append({
                "start_time": (datetime.datetime.now() - datetime.timedelta(days=days_ago,hours=3)).strftime("%Y-%m-%d %H:%M"),
                "end_time": (datetime.datetime.now() - datetime.timedelta(days=days_ago,hours=1)).strftime("%Y-%m-%d %H:%M"),
                "is_guest": False,
                "floor": f + 1,
                "position_num": r * ParkingSpec.COL.value + c + 1,
                "payment": 3500 if (r * ParkingSpec.COL.value + c + 1) % 2 == 0 else 6000,
            })

    # print(parking_state)
    # print(json.dumps(user_db, indent=2))
    # print("=" * 20)
    # print(json.dumps(user_history_db, indent=2))





def get_parking_number(row, col):
    """ 주차 번호 계산 """
    pass


def is_parking_able(floor, parking_number):
    """ 주차 가능 여부 확인 """
    pass


def view_current_parking_state():

    """ 주차 현황 조회"""
    for f in range(ParkingSpec.FLOOR.value-1, -1, -1):
        print("[" + str(f+1) + "F]")
        view_floor_parking_state(f+1)
        # for r in range(ParkingSpec.ROW.value):
        #     line = ""
        #     for c in range(ParkingSpec.COL.value):
        #         line += parking_state[f][r][c].value
        #     print(line)
        print()

    pass

# return parking fee


def view_floor_parking_state(floor):
    print(f"\n=== {floor}층 주차 현황 ===")
    for r in range(ParkingSpec.ROW.value + 1): # + 1 열 번호 자리
        if r == 0:
            row_display = "\t".join(str(c+1) for c in range(ParkingSpec.COL.value))
            print("\t" + row_display)
            continue
        row_display = "\t".join(parking_state[floor-1][r-1][c].value for c in range(ParkingSpec.COL.value))
        print(f"{r}\t" + row_display)


def enter(car_number):
    """ 차량 입차 """

    #이미 입차된 차량인지 확인
    if car_number in user_db:           
        print("이미 입차된 차량입니다.")
        return
    
    #층별 빈자리 안내
    for f in range(ParkingSpec.FLOOR.value):
        empty = 0                               #빈자리 변수
        for r in range(ParkingSpec.ROW.value):
            for c in range(ParkingSpec.COL.value):
                if parking_state[f][r][c] == ParkingImage.ABLE:
                    empty += 1
        print(f"{f+1}층 : 빈자리 {empty}개")
   
    #주차할 층 선택
    floor = int(input(f"원하는 층을 입력하세요 (1~{ParkingSpec.FLOOR.value}): "))
    if floor < 1 or floor > ParkingSpec.FLOOR.value: #범위에서 벗어나는지 확인
        print("잘못된 층 입력입니다.")
        return
    
    # 해당 층 주차 현황 출력 (임시 구현 view_current_parking_state()으로 변경 예정)
    view_floor_parking_state(floor)
    # print(f"\n=== {floor}층 주차 현황 ===")
    # for r in range(ParkingSpec.ROW.value + 1): # + 1 열 번호 자리
    #     if r == 0:
    #         row_display = "\t".join(str(c+1) for c in range(ParkingSpec.COL.value))
    #         print("   " + row_display)
    #         continue
    #     row_display = "\t".join(parking_state[floor-1][r][c].value for c in range(ParkingSpec.COL.value))
    #     print(f"{r}행: " + row_display)

    # 원하는 자리 선택
    row = int(input(f"원하는 행(1~{ParkingSpec.ROW.value}): "))
    col = int(input(f"원하는 열(1~{ParkingSpec.COL.value}): "))

    # 범위에서 벗어나는지 확인
    if row < 1 or row > ParkingSpec.ROW.value or col < 1 or col > ParkingSpec.COL.value:
        print("잘못된 좌석 입력입니다.")
        return
    
    # 빈자리 확인 후 배정
    if parking_state[floor-1][row-1][col-1] == ParkingImage.ABLE:
        parking_state[floor-1][row-1][col-1] = ParkingImage.DISABLE
        user_db[car_number] = {
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),  
            "end_time": "",
            "is_guest": True,
            "floor": floor,
            "position_num": (row-1) * ParkingSpec.COL.value + col #1~100까지 주차자리의 번호 
        }
        # 해당 층 주차 현황 출력 (임시 구현 view_current_parking_state()으로 변경 예정)
        view_floor_parking_state(floor)
        # print(f"\n=== {floor}층 주차 현황 ===")
        # for r in range(ParkingSpec.ROW.value):
        #   row_display = "\t".join(parking_state[floor-1][r][c].value for c in range(ParkingSpec.COL.value))
        #   print(row_display)

        print(f"{car_number} 차량이 {floor}층 ({row},{col}) 자리에 입차되었습니다.")
        
    else:
        print("이미 사용 중인 자리입니다.")

    pass

def payment(car_number):
    entry = user_db[car_number]
    start = datetime.datetime.strptime(entry['start_time'], "%Y-%m-%d %H:%M")
    end = datetime.datetime.now()
    duration = int((end - start).total_seconds() // 60)  # 분

    # 20분 이내 출차 시 추가요금 없음
    if duration <= 20:
        fee = 0
    else:
        fee = 5000
        if duration > 60:
            extra = duration - 60
            fee += ((extra + 29) // 30) * 500  # 30분 단위 반올림
        if fee > 20000:
            fee = 20000
        if not entry['is_guest']:  # 정기권 차량
            fee = fee // 2

    return fee, end.strftime("%Y-%m-%d %H:%M")


def leave(car_number):
    if car_number not in user_db:
        print("등록된 차량이 아닙니다. 다시 시도하세요.")
        return
    entry = user_db[car_number]
    fee, end_time = payment(car_number)
    print(f"차량번호: {car_number}, 주차요금: {fee}원")

    floor_idx = entry['floor'] - 1
    pos_idx = entry['position_num'] - 1
    r, c = divmod(pos_idx, ParkingSpec.COL.value)
    parking_state[floor_idx][r][c] = ParkingImage.ABLE  # 빈자리로 변경

    del user_db[car_number]

    view_current_parking_state()



def action_filter(input):
    for act in Action:
        if input in act.value.split(".") or input == act.value:
            # print(f"선택된 작업: {act.name}")
            return act


def main():
    init_parking_state()

    action = None

    while action != Action.EXIT:
        print("원하는 작업을 선택하세요:(입차:1, 출차:2, 시스템 종료:3)")
        user_input = input("입력: ").strip()
        action = action_filter(user_input)

        if action is None:
            print("잘못된 입력입니다. 다시 시도하세요.")
            continue

        if action == Action.ENTER:
            car_number = input("차량 번호를 입력하세요: ").strip()
            enter(car_number)
        elif action == Action.LEAVE:
            car_number = input("차량 번호를 입력하세요: ").strip()
            leave(car_number)
        elif action == Action.EXIT:
            print("시스템을 종료합니다.")
        else:
            print("알 수 없는 작업입니다.")

main()



# # view sample
# for f in range(ParkingSpec.FLOOR.value-1, -1, -1):
#     print(f"Floor {f+1}:")
#     for r in range(ParkingSpec.ROW.value):
#         row_display = "\t".join(
#             parking_state[f][r][c].value for c in range(ParkingSpec.COL.value))
#         print(row_display)
#     print("\n")

FLOORS = 10   # 층
COLS = 5      # 가로
ROWS = 3      # 세로

EMPTY = "🅿️"
CAR = "🚗"

def make_parking():
    parking = {}
    # 층 만들기
    for f in range(1, FLOORS+1):
        f_name = str(f) + "f"
        # 층 이름
        f_map = {} # 층 딕셔너리

        for r in range(1, ROWS+1):
            # 세로줄 만들기
            for c in range(1, COLS+1):
                # 가로줄 마늗릭
                if r == 2:   # 통로
                    f_map[(r,c)] = " "
                else:        # 주차 가능 자리
                    f_map[(r,c)] = EMPTY

        parking[f_name] = f_map
    return parking

def viewer(parking, floor):
    # 전체를 볼지 한 층만을 볼지
    if not floor:
        # 전체 층 보기(아무것도 입력 x)
        floors = parking.keys()
    else:
        floors = [str(floor) + "f"]

    for f in floors:
        # 실제 뷰어
        print("[" + f + "]")
        for r in range(1, ROWS+1):
            #세로 반복
            line = ""
            for c in range(1, COLS+1):
                # 가로 반복
                line += parking[f][(r,c)]
            print(line)
        print()
# 실행 예시
# p = make_parking()
# a = input('층을 입력하세요(전체 층은 빈칸 or 0 입력) : ')
# viewer(p, a)

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
    CHECK = "3.주차 현황 조회"
    EXIT = "4.시스템 종료"


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

class CarType(Enum):
    COMPACT = "1.소형"
    ELECTRIC = "2.전기"
    DISABLED = "3.장애인"
    NONE = "4.해당사항 없음"

car_type_discount = {
    CarType.NONE : 0,
    CarType.COMPACT: 0.2,
    CarType.ELECTRIC: 0.3,
    CarType.DISABLED: 0.4
}

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

def generate_korean_car_number():
    head_num = random.randint(100, 999)
    kor_chars = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하"]
    kor = random.choice(kor_chars)
    tail_num = random.randint(1000, 9999)
    return f"{head_num}{kor}{tail_num}"

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
        car_number = generate_korean_car_number()
        # use datetime

        car_type = CarType.NONE
        if idx % 4 == 0:
            car_type = CarType.COMPACT
        elif idx % 4 == 1:
            car_type = CarType.DISABLED
        elif idx % 4 == 2:
            car_type == CarType.ELECTRIC
        user_db[car_number] = {
            "start_time": (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1,10))).strftime("%Y-%m-%d %H:%M"),
            "end_time": "",
            "is_guest": False,
            "floor": f + 1,
            "position_num": r * ParkingSpec.COL.value + c + 1,
            "car_type": car_type
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
                "car_type": car_type
            })

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
        print()
    pass


def view_floor_parking_state(floor, highlight=None):
    print(f"\n=== {floor}층 주차 현황 ===")
    for r in range(ParkingSpec.ROW.value + 1): # + 1 열 번호 자리
        if r == 0:
            row_display = "\t".join(str(c+1) for c in range(ParkingSpec.COL.value))
            print("\t" + row_display)
            continue
        row_elems = []
        for c in range(ParkingSpec.COL.value):
            if highlight and (r-1, c) == highlight:
                row_elems.append("🚙")  # 강조 자리만 🚙로 출력
            else:
                row_elems.append(parking_state[floor-1][r-1][c].value)
        print(f"{r}\t" + "\t".join(row_elems))


def enter(car_number):
    """ 차량 입차 """
    #이미 입차된 차량인지 확인
    if car_number in user_db:           
        print("이미 입차된 차량입니다.")
        return
    
    #층별 빈자리 안내
    while True:
        # 층별 빈자리 안내
        for f in range(ParkingSpec.FLOOR.value):
            empty = 0  # 빈자리 변수
            for r in range(ParkingSpec.ROW.value):
                for c in range(ParkingSpec.COL.value):
                    if parking_state[f][r][c] == ParkingImage.ABLE:
                        empty += 1
            print(f"{f+1}층 : 빈자리 {empty}개")

        # 주차할 층 선택
        floor = int(input(f"원하는 층을 입력하세요 (1~{ParkingSpec.FLOOR.value}): "))
        if floor < 1 or floor > ParkingSpec.FLOOR.value:
            print("잘못된 층 입력입니다.")
            continue

        # 해당 층 주차 현황 출력
        view_floor_parking_state(floor)

        # 원하는 자리 선택
        row = int(input(f"원하는 행(1~{ParkingSpec.ROW.value}): "))
        col = int(input(f"원하는 열(1~{ParkingSpec.COL.value}): "))

        car_type = None
        while car_type == None:
            car_type_input = input(f"차량 종류를 입력하세요 ({', '.join([ct.value for ct in CarType])}): ")
            car_type = car_type_input_filter(car_type_input)
            if car_type is None:
                print("잘못된 차량 종류입니다. 다시 시도하세요.")
            else:
                break

        # 범위에서 벗어나는지 확인
        if row < 1 or row > ParkingSpec.ROW.value or col < 1 or col > ParkingSpec.COL.value:
            print("잘못된 좌석 입력입니다.")
            continue

        # 빈자리 확인 후 배정
        if parking_state[floor-1][row-1][col-1] == ParkingImage.ABLE:
            parking_state[floor-1][row-1][col-1] = ParkingImage.DISABLE
            user_db[car_number] = {
                "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "end_time": "",
                "is_guest": True,
                "floor": floor,
                "position_num": (row-1) * ParkingSpec.COL.value + col,  # 1~100까지 주차자리의 번호
                "car_type" : car_type if car_type != None else ""
            }

            view_floor_parking_state(floor, highlight=(row-1, col-1))
            print(f"{car_number} 차량이 {floor}층 ({row},{col}) 자리에 입차되었습니다.")
            break  # 입차 완료 시 반복문 종료
        else:
            print("이미 사용 중인 자리입니다. 다시 선택해주세요.")

def payment(car_number):
    entry = user_db[car_number]
    

    car_type = car_type_value_to_enum(entry["car_type"])
    
    start = datetime.datetime.strptime(entry['start_time'], "%Y-%m-%d %H:%M")
    end = datetime.datetime.now()
    duration = int((end - start).total_seconds() // 60)  # 분

    temp_fee = 0
    # 20분 이내 출차 시 추가요금 없음
    if duration <= 20:
        fee = 0
    else:
        fee = 5000
        temp_fee = fee
        if duration > 60:
            extra = duration - 60
            fee += ((extra + 29) // 30) * 500  # 30분 단위 반올림
            temp_fee = fee
        if fee > 20000:
            fee = 20000
            temp_fee = fee
        if not entry['is_guest']:  # 정기권 차량
            fee = fee // 2
    
    # cat_type discount
    if car_type is not None and car_type != CarType.NONE:
        fee -= temp_fee * car_type_discount[car_type]


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

    view_floor_parking_state(entry['floor'], highlight=(r, c))

    parking_state[floor_idx][r][c] = ParkingImage.ABLE  # 빈자리로 변경

    del user_db[car_number]

    view_current_parking_state()



def car_type_value_to_enum(str):
    if str == CarType.COMPACT.value:
        return CarType.COMPACT
    elif str == CarType.ELECTRIC.value:
        return CarType.ELECTRIC
    elif str == CarType.DISABLED.value:
        return CarType.DISABLED
    elif str == CarType.NONE.value:
        return CarType.NONE
    return None
def car_type_input_filter(input):
    for type in CarType:
        if input in type.value.split(".") or input == type.value:
            # print(f"선택된 작업: {type.name}")
            return type 
def action_filter(input):
    for act in Action:
        if input in act.value.split(".") or input == act.value:
            # print(f"선택된 작업: {act.name}")
            return act


def main():
    init_parking_state()

    action = None
    print("안녕하세요 삼각편대 주차 타워 시스템 입니다.")
    while action != Action.EXIT:
    
        print("원하는 작업을 선택하세요:(입차:1, 출차:2, 주차장 현황:3, 시스템 종료:)")
        user_input = input("입력: ").strip()
        action = action_filter(user_input)

        if action is None:
            print("잘못된 입력입니다. 다시 시도하세요.")
            continue

        if action == Action.ENTER:
            car_number = input("차량 번호를 입력하세요: ").strip()
            enter(car_number)
        elif action == Action.LEAVE:
            print("현재 입차 중인 차량 목록:")
            for car in user_db:
                print("-", car)
            car_number = input("차량 번호를 입력하세요: ").strip()
            leave(car_number)
        elif action == Action.CHECK:
            view_current_parking_state()
        elif action == Action.EXIT:
            print("시스템을 종료합니다.")
        else:
            print("알 수 없는 작업입니다.")

main()
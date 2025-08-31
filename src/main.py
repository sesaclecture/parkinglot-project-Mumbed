
""" 
주차 관리 시스템
"""
from enum import Enum
import random
import datetime


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

# 3차원 배열 [floor][row][col]
parking_state = []

def init_parking_state():
    """
      주차 상태 초기화
      dummy data
    """
    global parking_state
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

    for f, r, c in disable_positions:
        parking_state[f][r][c] = ParkingImage.DISABLE
    
    # print(parking_state)

# 차량 정보 DB (임시)
# 차량번호: car_num0
user_db = {
    "car_num0": {
        # yyyy-mm-dd HH:MM
        "start_time": "2023-01-01 10:00",
        "end_time": "",
        "is_guest": False,
        "floor": 1,
        # 0 < position_num and position_num < row x col
        "position_num": 2,
    }
}


def get_parking_number(row, col):
    """ 주차 번호 계산 """
    pass


def is_parking_able(floor, parking_number):
    """ 주차 가능 여부 확인 """
    pass


def view_current_parking_state():
    """주차 현황 조회"""
    pass

# return parking fee
def payment(car_number):
    """
## 시나리오 1
1. 정기권 보유한 사용자 입차
1. 차량번호, 입차 시각, 원하는 주차위치 (층/번호) 입력
2. 1F 빈자리 4번째 자리로 안내 받은 뒤 선택
3. 3시간 후 출차  주차비용 3500원 계산
4. 출차

## 시나리오 2
1. 정기권 보유한 사용자 입차
    1. 차량번호, 입차 시각, 원하는 주차위치 (층/번호) 입력
2. 2F 빈자리 1번째 자리로 안내 받은 뒤 선택
3. 2시간 후 출차  주차비용 6000원 계산
4. 출차

# 주차 요금
- 회차 불가
- 입차 후 60분까지 5000원
- 이후 30분당 500원
- 일일 최대 비용 20000원
- 정기권 사용자 일 주차 비용 50%적용
"""
    pass


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
    print(f"\n=== {floor}층 주차 현황 ===")
    for r in range(ParkingSpec.ROW.value):
        row_display = "\t".join(parking_state[floor-1][r][c].value for c in range(ParkingSpec.COL.value))
        print(row_display)

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
            "start_time": datetime.datetime.now,  
            "end_time": "",
            "is_guest": True,
            "floor": floor,
            "position_num": (row-1) * ParkingSpec.COL.value + col #1~100까지 주차자리의 번호 
        }
        print(f"{car_number} 차량이 {floor}층 ({row},{col}) 자리에 입차되었습니다.")
    else:
        print("이미 사용 중인 자리입니다.")

    pass


def leave(car_number):
    """ 차량 출차 """
    pass


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
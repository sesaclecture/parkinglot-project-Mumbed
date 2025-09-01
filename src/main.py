"""
주차 관리 시스템
"""
from enum import Enum
import datetime
import json
import os
import random
import re


class Action(Enum):
    ENTER = "1.입차"
    LEAVE = "2.출차"
    CHECK = "3.주차 현황 조회"
    GUEST = "4.정기권 구매"
    RESERVE = "5.예약"
    EXIT = "6.시스템 종료"


class ParkingImage(Enum):
    ABLE = "🅿️"
    DISABLE = "🚗"


class ParkingSpec(Enum):
    FLOOR = 3
    ROW = 10
    COL = 10


class CarType(Enum):
    COMPACT = "1.소형"
    ELECTRIC = "2.전기"
    DISABLED = "3.장애인"
    NONE = "4.해당사항 없음"


car_type_discount = {
    CarType.NONE: 0,
    CarType.COMPACT: 0.2,
    CarType.ELECTRIC: 0.3,
    CarType.DISABLED: 0.4
}


def generate_korean_car_number():
    head_num = random.randint(100, 999)
    kor_chars = ["가", "나", "다", "라", "마", "바","사", "아", "자", "차", "카", "타", "파", "하"]
    kor = random.choice(kor_chars)
    tail_num = random.randint(1000, 9999)
    return f"{head_num}{kor}{tail_num}"

def is_valid_car_number(car_number):
    pattern = re.compile(r"^\d{2,3}[가-힣]\d{4}$")  # 2-3자리 숫자 + 한글 1자 + 4자리 숫자
    return bool(pattern.match(car_number))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/
DATA_FILE = os.path.join(BASE_DIR, "..", "parking_data.json")


# 3차원 배열 [floor][row][col]
parking_state = []
user_db = {}
user_history_db = {}
user_reserve_db = {}


def save_data_to_file(user_db, user_history_db, filename=DATA_FILE):
    data = {
        "user_db": user_db,
        "user_history_db": user_history_db,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_data_from_file(filename=DATA_FILE):
    if not os.path.exists(filename):
        return {}, {}
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("user_db", {}), data.get("user_history_db", {})


def init_parking_state():
    global parking_state, user_db, user_history_db

    user_db_loaded, user_history_db_loaded = load_data_from_file()

    if user_db_loaded:
        user_db.update(user_db_loaded)
        user_history_db.update(user_history_db_loaded)
        print("저장된 데이터에서 차량 정보를 불러왔습니다.")
    else:
        user_db.clear()
        user_history_db.clear()
        print("저장된 데이터가 없습니다. 현재 차량 데이터는 비어있습니다.")

    parking_state[:] = [
        [
            [ParkingImage.ABLE for _ in range(ParkingSpec.COL.value)]
            for _ in range(ParkingSpec.ROW.value)
        ]
        for _ in range(ParkingSpec.FLOOR.value)
    ]

    for car_info in user_db.values():
        f = car_info["floor"] - 1
        pos = car_info["position_num"] - 1
        r, c = divmod(pos, ParkingSpec.COL.value)
        parking_state[f][r][c] = ParkingImage.DISABLE


def get_parking_number(row, col):
    """주차 번호 계산"""
    return (row - 1) * ParkingSpec.COL.value + col


def is_parking_able(floor, parking_number):
    floor_idx = floor - 1
    pos_idx = parking_number - 1
    r, c = divmod(pos_idx, ParkingSpec.COL.value)
    return parking_state[floor_idx][r][c] == ParkingImage.ABLE


def view_current_parking_state():
    """주차 현황 조회"""
    for f in range(ParkingSpec.FLOOR.value - 1, -1, -1):
        print(f"[{f + 1}F]")
        view_floor_parking_state(f + 1)
        print()


def view_floor_parking_state(floor, highlight=None):
    print(f"\n=== {floor}층 주차 현황 ===")
    for r in range(ParkingSpec.ROW.value + 1):
        if r == 0:
            row_display = "\t".join(str(c + 1) for c in range(ParkingSpec.COL.value))
            print("\t" + row_display)
            continue
        row_elems = []
        for c in range(ParkingSpec.COL.value):
            if highlight and (r - 1, c) == highlight:
                row_elems.append("🚙")  # 강조 자리만 🚙로 출력
            else:
                row_elems.append(parking_state[floor - 1][r - 1][c].value)
        print(f"{r}\t" + "\t".join(row_elems))


def car_type_input_filter(user_input):
    for ct in CarType:
        if user_input == ct.value.split(".")[0] or user_input == ct.value:
            return ct
    return None


def car_type_value_to_enum(value_str):
    for ct in CarType:
        if ct.value == value_str:
            return ct
    return None


def enter(car_number):
    """차량 입차"""
    if not is_valid_car_number(car_number):
        print("[오류] 차량 번호 형식이 올바르지 않습니다. 예: 12다1234, 123구1234")
        return
    if car_number in user_db:
        print("[오류] 이미 입차된 차량번호입니다.")
        return

    while True:
        total_empty = 0
        for f in range(ParkingSpec.FLOOR.value):
            empty = sum(
                parking_state[f][r][c] == ParkingImage.ABLE
                for r in range(ParkingSpec.ROW.value)
                for c in range(ParkingSpec.COL.value)
            )
            print(f"{f + 1}층 : 빈 자리 {empty}개")
            total_empty += empty
        if total_empty == 0:
            print("[안내] 현재 주차장에 빈자리가 없습니다. 예약을 이용해주세요.")
            return

        try:
            floor = int(input(f"원하는 층을 입력하세요 (1~{ParkingSpec.FLOOR.value}): ").strip())
            if not (1 <= floor <= ParkingSpec.FLOOR.value):
                print("[오류] 올바른 층 번호를 입력하세요.")
                continue
        except ValueError:
            print("[오류] 숫자만 입력 가능합니다. 다시 시도하세요.")
            continue

        view_floor_parking_state(floor)

        try:
            row = int(input(f"원하는 행(1~{ParkingSpec.ROW.value}): ").strip())
            col = int(input(f"원하는 열(1~{ParkingSpec.COL.value}): ").strip())
            if not (1 <= row <= ParkingSpec.ROW.value and 1 <= col <= ParkingSpec.COL.value):
                print("[오류] 행과 열은 지정된 범위 내 숫자여야 합니다.")
                continue
        except ValueError:
            print("[오류] 숫자만 입력 가능합니다. 다시 시도하세요.")
            continue

        # 차량 타입 입력 및 검증
        car_type = None
        while True:
            car_type_input = input(f"차량 종류를 입력하세요 ({', '.join([ct.value for ct in CarType])}): ").strip()
            car_type = car_type_input_filter(car_type_input)
            if car_type is None:
                print("[오류] 올바른 차량 종류를 선택해주세요.")
            else:
                break

        if parking_state[floor - 1][row - 1][col - 1] == ParkingImage.ABLE:
            parking_state[floor - 1][row - 1][col - 1] = ParkingImage.DISABLE
            user_db[car_number] = {
                "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "end_time": "",
                "is_guest": True,
                "floor": floor,
                "position_num": (row - 1) * ParkingSpec.COL.value + col,
                "car_type": car_type.value
            }
            save_data_to_file(user_db, user_history_db)

            view_floor_parking_state(floor, highlight=(row - 1, col - 1))
            print(f"[성공] {car_number} 차량이 {floor}층 ({row},{col}) 자리에 입차되었습니다.")
            break
        else:
            print("[오류] 선택하신 자리는 이미 사용 중입니다. 다른 자리를 선택해주세요.")


def Reserve(car_number):
    if car_number in user_reserve_db:
        print("[오류] 이미 예약된 차량입니다.")
        return

    while True:
        enter_reserve_time = input("예약 입차일시(ex: 2025-08-27 10:58): ").strip()
        try:
            enter_reserve_datetime = datetime.datetime.strptime(enter_reserve_time, "%Y-%m-%d %H:%M")
        except ValueError:
            print("[오류] 날짜 및 시간 형식이 올바르지 않습니다. 다시 시도하세요.")
            continue

        current_datetime = datetime.datetime.now()
        if enter_reserve_datetime < current_datetime + datetime.timedelta(days=1):
            print("[오류] 예약은 최소 하루 전부터 가능합니다. 다시 시도하세요.")
            continue

        leave_reserve_time = input("예약 출차일시(예: 2025-08-27 10:58): ").strip()
        try:
            leave_reserve_datetime = datetime.datetime.strptime(leave_reserve_time, "%Y-%m-%d %H:%M")
        except ValueError:
            print("[오류] 날짜 및 시간 형식이 올바르지 않습니다. 다시 시도하세요.")
            continue

        if leave_reserve_datetime <= enter_reserve_datetime:
            print("[오류] 출차시간은 입차시간 이후여야 합니다. 다시 시도하세요.")
            continue

        user_reserve_db[car_number] = {
            "enter_reserve_time": enter_reserve_time,
            "leave_reserve_time": leave_reserve_time
        }
        print(f"[성공] {car_number} 예약이 완료되었습니다.")
        break


def payment(car_number):
    entry = user_db[car_number]

    car_type = car_type_value_to_enum(entry.get("car_type", CarType.NONE.value))

    start = datetime.datetime.strptime(entry['start_time'], "%Y-%m-%d %H:%M")
    end = datetime.datetime.now()
    duration = int((end - start).total_seconds() // 60)  # 분

    temp_fee = 0
    if duration <= 20:
        fee = 0
    else:
        fee = 5000
        temp_fee = fee
        if duration > 60:
            extra = duration - 60
            fee += ((extra + 29) // 30) * 500
            temp_fee = fee
        if not entry['is_guest']:
            fee = fee // 2

    # 차량 타입에 따른 할인 적용
    if car_type and car_type != CarType.NONE:
        discount_rate = car_type_discount.get(car_type, 0)
        discount_amount = temp_fee * discount_rate
        fee = max(0, int(fee - discount_amount))

    return fee, end.strftime("%Y-%m-%d %H:%M")


def leave(car_number):
    if car_number not in user_db:
        print("[오류] 등록된 차량이 아닙니다. 다시 시도해주세요.")
        return

    fee, end_time = payment(car_number)
    print(f"[정산] 차량번호: {car_number}, 주차요금: {fee}원")

    entry = user_db[car_number]
    floor_idx = entry['floor'] - 1
    pos_idx = entry['position_num'] - 1
    r, c = divmod(pos_idx, ParkingSpec.COL.value)

    view_floor_parking_state(entry['floor'], highlight=(r, c))

    parking_state[floor_idx][r][c] = ParkingImage.ABLE

    if car_number not in user_history_db:
        user_history_db[car_number] = []

    user_history_db[car_number].append({
        "start_time": entry["start_time"],
        "end_time": end_time,
        "is_guest": entry["is_guest"],
        "floor": entry["floor"],
        "position_num": entry["position_num"],
        "payment": fee,
        "car_type": entry.get("car_type", CarType.NONE.value)
    })

    del user_db[car_number]

    save_data_to_file(user_db, user_history_db)

    view_current_parking_state()


def action_filter(user_input):
    for act in Action:
        if user_input == act.value.split(".")[0] or user_input == act.value:
            return act
    return None


def make_is_guest():
    print("정기권 구매 페이지입니다. 입차 후 이용해주세요.")
    car_num = input("차량 번호를 입력해주세요: ").strip()
    if car_num not in user_db:
        print("[오류] 입차 신청 후 이용 가능합니다.")
        return

    guest_time = input("구매하실 정기권 기간을 입력해주세요. (한달:1, 1년:2): ").strip()
    if guest_time not in ("1", "2"):
        print("[오류] 올바른 기간을 입력하세요 (1 또는 2).")
        return

    entry = user_db[car_num]
    start_dt = datetime.datetime.strptime(entry['start_time'], "%Y-%m-%d %H:%M")

    if guest_time == "1":
        end_dt = start_dt + datetime.timedelta(days=30)
        print("한달 정기권 요금: 월 7만원")
    else:
        end_dt = start_dt + datetime.timedelta(days=365)
        print("1년 정기권 요금: 60만원 (월 5만원)")

    card = input("카드를 넣고 Enter를 누르세요: ").strip()
    if card == "":
        user_db[car_num]["is_guest"] = False
        save_data_to_file(user_db, user_history_db)
        print(f"[성공] 정기권 적용 기간: {start_dt.strftime('%Y-%m-%d')} ~ {end_dt.strftime('%Y-%m-%d')}")


def main():
    init_parking_state()

    print("안녕하세요 삼각편대 주차 타워 시스템입니다.")
    action = None
    while action != Action.EXIT:
        print("\n원하는 작업을 선택하세요:")
        print("1.입차, 2.출차, 3.주차장 현황 조회, 4.정기권 구매, 5.주차장 예약, 6.시스템 종료")

        user_input = input("입력: ").strip()
        action = action_filter(user_input)

        if action is None:
            print("[오류] 올바른 메뉴 번호를 입력해주세요.")
            continue

        if action == Action.ENTER:
            car_number = input("차량 번호를 입력하세요: ").strip()
            if not car_number:
                print("[오류] 차량 번호는 필수 입력값입니다.")
                continue
            enter(car_number)

        elif action == Action.LEAVE:
            if not user_db:
                print("[안내] 현재 주차 중인 차량이 없습니다.")
                continue
            print("현재 입차 중인 차량 목록:")
            cars = list(user_db.keys())
            for car in cars[:5]:
                print(" -", car)
            if len(cars) > 5:
                print(" ...")
            car_number = input("출차할 차량 번호를 입력하세요: ").strip()
            if not car_number:
                print("[오류] 차량 번호를 입력해주세요.")
                continue
            leave(car_number)

        elif action == Action.CHECK:
            view_current_parking_state()

        elif action == Action.GUEST:
            make_is_guest()

        elif action == Action.RESERVE:
            car_number = input("예약할 차량 번호를 입력하세요: ").strip()
            if not car_number:
                print("[오류] 차량 번호를 입력해주세요.")
                continue
            Reserve(car_number)

        elif action == Action.EXIT:
            print("시스템을 종료합니다. 이용해 주셔서 감사합니다.")
            break

        else:
            print("[오류] 알 수 없는 작업입니다. 다시 시도해주세요.")


if __name__ == "__main__":
    main()

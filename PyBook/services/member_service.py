# services/member_service.py 맨 위에 추가
import sys
from pathlib import Path

# 현재 파일의 부모의 부모 폴더(즉, PyBook 최상위 폴더)를 파이썬 검색 경로에 추가
sys.path.append(str(Path(__file__).resolve().parent.parent))
###########################################################

# services/member_service.py
from datetime import datetime
from models.member import Member
# from utils.file_handler import load_json, save_json
from utils.file_handler import FileHandler

import string

MEMBERS_FILE = "data/members.json"

def _get_members() -> list:
    # json파일에서 회원 데이터를 Member 객체 리스트로 반환합니다.
    data = FileHandler.load_json(MEMBERS_FILE)
    if isinstance(data, list):
        return[Member.from_dict(item) for item in data]
    return[]

def _save_members(members: list[Member]) -> None:
    #Member 객체 리스트를 딕셔너리로 변환하여 JSON파일에 저장합니다.
    data = [member.to_dict() for member in members]
    FileHandler.save_json(MEMBERS_FILE, data)

# 회원 아이디(이메일) 검증
def is_valid_email(email: str) -> bool:
    # 문자열 타입 검증
    if not isinstance(email,str):
        return False
    # 길이검증(5자 이상)
    if len(email) < 5:
        return False


    return True

# 비밀번호 검증하기
def is_valid_pw(pw: str) -> bool:
    # 길이검증(5자 이상)
    if len(pw) < 5:
        return False
    # 특수문자 포함 여부 검증
    has_special = any(char in string.punctuation for char in pw)
    if not has_special:
        return False

    return True


# 연락처 검증하기
def is_valid_phone(phone: str) -> bool:
    # 문자열 타입 검증
    if not isinstance(phone, str):
        return False
    # 하이픈(-)과 공백 제거
    clean_phone = phone.replace("-", "").replace(" ", "")

    # 숫자로만 이루어졌는지 확인
    if not clean_phone.isdigit():
        return False

    # 010으로 시작하는지 확인 (국내 휴대전화 표준)
    if not clean_phone.startswith("010"):
        return False

    # 010 포함 총 11자리인지 확인
    if len(clean_phone) != 11:
        return False

    return True


#회원가입
#회원가입하는 아이디(이메일)가 기존의 있는 아이디인지 검증해야합니다.
#비밀번호 해싱 암호화 부분은 구현어려우시면 일단 비밀번호 그대로 members.json에 넣으셔도 됩니다. 나중에 제가 따로 함수 만들어 드리겠습니다.
#비밀번호는 비밀번호 확인(2차입력) 받으셔야 합니다.
# signup 함수 선언부 매개변수에 기본값 = "" 추가
def signup(email: str = "", pw: str = "", name: str = "", phone: str = "", interest: str = "") -> bool:
     
    members = _get_members()

    print("\n---[회원가입]---")

    # 이메일(아이디) 입력 & 검증
    while True:
        email_input = input("아이디 입력(이메일 형식): ").strip()

        # 이메일 양식 검증
        if not is_valid_email(email_input):
            print("[오류] 아이디는 @를 포함한 5글자 이상으로 입력하세요.")
            continue

        # 중복 확인
        is_duplicate = any(m.email == email_input for m in members)
        if is_duplicate:
            print("[오류] 이미 존재하는 아이디입니다. 다시 입력해주세요.")
            continue

        break
    print(f"아이디 입력 완료: {email_input}")

    # 비밀번호 입력 & 검증
    while True:
        pw_input = input("비밀번호 입력: ").strip()

        if not pw_input:
            print("[오류] 비밀번호는 필수 입력 항목입니다.")
            continue

        if not is_valid_pw(pw_input):
            print("[오류] 비밀번호는 5자 이상이며, 특수문자를 최소 1개 이상 포함해야 합니다.")
            continue

        # 비밀번호 2차 확인
        pw_confirm = input("비밀번호 확인을 위해 한 번 더 입력해주세요: ").strip()
        if pw_input != pw_confirm:
            print("[오류] 입력하신 비밀번호가 서로 일치하지 않습니다. 다시 입력해주세요.")
            continue

        break

    # 이름 입력
    while True:
        name_input = input("이름 입력: ").strip()
        if not name_input:
            print("[오류] 이름은 필수 입력 항목입니다.")
            continue
        break

    # 연락처 입력 & 검증
    while True:
        phone_input = input("연락처 입력(- 제외 숫자 11자리): ").strip()
        if not is_valid_phone(phone_input):
            print("[오류] 연락처는 숫자 11자리로 입력해야 합니다. (예: 01012345678)")
            continue
        break

    # 관심분야 입력 (선택)
    interest_input = input("관심분야를 입력하세요 (선택): ").strip()

    
    # Member 객체 생성 및 JSON 파일 저장
    new_member = Member(
        email=email_input,
        pw=pw_input,
        name=name_input,
        phone=phone_input,
        interest=interest_input
    )

    # 리스트에 추가 후 파일 저장
    members.append(new_member)
    _save_members(members)

    print(f'{name_input}님, 회원가입이 완료되었습니다!')
    return True

#로그인
def login(email: str, pw: str) -> dict | None:
    members = _get_members()

    for member in members:
        if member.email == email:
            if member.pw == pw:
                print(f'{member.name}님, 환영합니다!')
                return member.to_dict()
            else:
                print("비밀번호가 올바르지 않습니다.")
                return None
            
    print("존재하지 않는 이메일 계정입니다.")
    return None

# 회원 정보 수정

def update_user(email: str, **kwargs)->bool:
    #kwargs 형태로 전달받은 회원정보를 업데이트합니다.
    members = _get_members()
    updated_member = None # 수정 대상 회원

    # 수정할 회원 찾기
    for member in members:
        if member.email == email:
            updated_member = member
            break

    if updated_member is None:
        print("[오류] 해당 회원을 찾을 수 없습니다.")
        return False

    updated = False

    # kwargs에 넘겨받은 항목들 업데이트 처리
    # pw 수정인 경우 유효성 검사
    if 'pw' in kwargs and kwargs['pw']:
        new_pw = kwargs["pw"]
        if not is_valid_pw(new_pw):
            print(
                "[오류] 새 비밀번호는 5자 이상이며, 특수문자를 최소 1개 이상 포함해야 합니다."
            )
            return False

        pw_confirm = input(
            "새 비밀번호 확인을 위해 한 번 더 입력해주세요: "
        ).strip()
        if new_pw != pw_confirm:
            print("[오류] 입력하신 비밀번호가 일치하지 않습니다.")
            return False

        updated_member.pw = new_pw
        updated = True

    # 이름(name) 수정
    if "name" in kwargs and kwargs["name"]:
        updated_member.name = kwargs["name"]
        updated = True

    # 연락처(phone) 수정
    if "phone" in kwargs and kwargs["phone"]:
        new_phone = kwargs["phone"]
        if not is_valid_phone(new_phone):
            print(
                "[오류] 연락처는 숫자 11자리로 입력해야 합니다. (예:01012345678)"
            )
            return False
        updated_member.phone = new_phone
        updated = True

    # 관심분야 수정
    if "interest" in kwargs and kwargs["interest"]:
        updated_member.interest = kwargs["interest"]
        updated = True

    # 뱐경사항 저장
    if updated:
        _save_members(members)
        print(f"[성공] 회원 정보가 성공적으로 수정되었습니다!")
        return True
    else:
        print("[알림] 변경할 항목이 없거나 올바르지 않습니다.")
        return False



#로그아웃
#로그아웃기능은 아마 함수로 구현할 부분은 없을 가능성이 높습니다.
#main에서 세션관리부분만 초기화시키고 처음 홈화면으로 이동시키면 될거같습니다
def logout(email: str) -> bool:
    # 콘솔 프로그램 특성상 세션 관리는 main.py에서 주로 담당하므로 True 반환
    return True

#회원탈퇴
#구현 시 정말 탈퇴하시겠습니까? 같은 문자 출력후 비밀번호 입력하면 json파일에서 회원정보 삭제하는식으로 탈퇴시키면됩니다.
#회원 탈퇴 후에는 홈화면으로 이동하게됩니다.
def withdraw(email: str, pw: str) -> bool:
    pass


#회원 정보 수정은 우선 함수 한개로 구성해놓았는데 
#구현 하실 때 비밀번호 재설정과 phone,interest,name 부분 수정으로 함수 두개로 나눠서 구현하셔도 됩니다.
def update(email: str, **kwargs) -> bool:
    pass



# ==========================================
#테스트 코드
# ==========================================
if __name__ == "__main__":
#     print("=" * 50)
#     print("회원가입 테스트")
#     print("=" * 50)
   
#     signup()
   
#     ######################
#     print("=" * 50)
#     print("로그인 테스트")
#     print("=" * 50)

#     while True:
#         print("\n--- [ 로그인 ] ---")
#         login_email = input("아이디(이메일) 입력: ").strip()
#         login_pw = input("비밀번호 입력: ").strip()

#         # 로그인 시도
#         user_data = login(login_email, login_pw)

#         if user_data:
#             print(f"\n[로그인 성공 데이터 반환 확인]: {user_data}")
#             break
#         else:
#             retry = input("\n다시 로그인하시겠습니까? (Y/N): ").strip().upper()
#             if retry != "Y":
#                 print("로그인 테스트를 종료합니다.")
#                 break
    
    ######################
    print("=" * 50)
    print("회원정보수정 테스트")
    print("=" * 50)

    login_email = input("\n정보 수정할 계정(이메일) 입력: ").strip()
    login_pw = input("비밀번호 입력: ").strip()

    user_info = login(login_email, login_pw)

    if user_info:
        print("\n--- [ 회원 정보 수정 메뉴 ] ---")
        print("1. 이름/연락처/관심분야 수정")
        print("2. 비밀번호 변경")

        choice = input("메뉴 선택: ").strip()

        if choice == "1":
            new_name = input("새 이름 입력 (엔터 시 유지): ").strip()
            new_phone = input("새 연락처 입력 (-제외 11자리, 엔터 시 유지): ").strip()
            new_interset = input("새 관심분야 입력 (엔터 시 유지): ").strip()

            update(
                login_email,
                name = new_name if new_name else None,
                phone = new_phone if new_phone else None,
                interest = new_interset if new_interset else None
            )

        elif choice == "2":
            new_pw = input("변경할 새 비밀번호 입력: ").strip()
            update(login_email,pw = new_pw)

        # 수정 결과 확인
        print("\n[최종 업데이트 데이터 확인]")
        updated_user = login(login_email,login_pw if choice != "2" else new_pw)
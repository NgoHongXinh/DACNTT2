
from passlib.context import CryptContext

from api.library.constant import FRIEND, PENDDING, NOT_FRIEND, WAIT_ACCEPT
from api.third_parties.database.query.friend_request import get_friend

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# current user: người hiện tại đang onl vaf vào trang 1 người nào đó => current_user sẽ là người gửi lời mời
# user_code_check: code cử người được ghé thăm => sẽ là người nhận được lời mời
async def check_friend_or_not_in_profile(current_user, user_code_check, list_friend_code):
    print(user_code_check , list_friend_code)
    if user_code_check in list_friend_code:
        return FRIEND
    else:
        check_is_send_request_or_not = await get_friend(current_user, user_code_check)
        check_current_user_receive_send_friend_request = await get_friend(user_code_check, current_user)
        print(check_current_user_receive_send_friend_request)
        if check_is_send_request_or_not and not check_current_user_receive_send_friend_request:
            return PENDDING
        if check_current_user_receive_send_friend_request and not check_is_send_request_or_not:
            return WAIT_ACCEPT
        return NOT_FRIEND



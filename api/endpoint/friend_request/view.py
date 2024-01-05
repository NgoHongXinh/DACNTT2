import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.friend_request.schema import ResponseFriendRequest
from api.library.constant import CODE_ERROR_USER_CODE_NOT_FOUND, CODE_ERROR_INPUT, \
    CODE_ERROR_WHEN_UPDATE_CREATE, CODE_ERROR_SERVER, CODE_ERROR_WHEN_UPDATE_CREATE_NOTI, \
    CODE_ERROR_WHEN_UPDATE_CREATE_FRIEND_REQUEST, CODE_SUCCESS, TYPE_MESSAGE_RESPONSE
from api.third_parties.database.model.friend_request import FriendRequest
from api.third_parties.database.model.notification import Notification
from api.third_parties.database.query.friend_request import get_friend, create_fr
from api.third_parties.database.query.notification import create_noti
from api.third_parties.database.query.user import get_user_by_code
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
@router.post(
    path="/friend_request/{user_code_want_request}",
    name="request_new_frient",
    description="send request friend to new people",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseFriendRequest],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_friend_request(user_code_want_request: str, user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        if not user_code_want_request:
            status_code = HTTP_400_BAD_REQUEST
            message = 'friend_request_id not allow empty'
            code = CODE_ERROR_INPUT
            raise HTTPException(status_code)
        user_want_request_friend = await get_user_by_code(user_code_want_request)
        if not user_want_request_friend:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            raise HTTPException(status_code)

        # kiểm tra xem 2 người đã là bạn bè hay chưa
        if user_want_request_friend in user['friends']:
            status_code = HTTP_400_BAD_REQUEST
            message = f"user code = {user_code_want_request} is already your friend"
            code = CODE_ERROR_INPUT
            raise HTTPException(status_code)

        friend_request = await get_friend(user['user_code'], user_code_want_request)
        if friend_request:
            status_code = HTTP_400_BAD_REQUEST
            message = "you already send request friend to this people"
            code = CODE_ERROR_INPUT
            raise HTTPException(status_code)

        friend_request_data = FriendRequest(
            friend_request_code=str(uuid.uuid4()),
            user_code_request=user['user_code'],
            user_code_receive=user_code_want_request,
            status=False
        )
        new_friend_request = await create_fr(friend_request_data)
        if new_friend_request:
            notification = Notification(
                notification_code=str(uuid.uuid4()),
                user_code=user_code_want_request,
                user_code_guest=user['user_code'],
                content='đã gửi lời mời kết bạn',

            )
            new_noti = await create_noti(notification)
            if not new_noti:
                status_code = HTTP_400_BAD_REQUEST
                code = CODE_ERROR_WHEN_UPDATE_CREATE_NOTI
                raise HTTPException(status_code)
            return SuccessResponse[ResponseFriendRequest](**{
                "data": {"message":"Send request success"},
                "response_status": {
                    "code": CODE_SUCCESS,
                    "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }})
        else:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_FRIEND_REQUEST
            raise HTTPException(status_code)
    except:
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )
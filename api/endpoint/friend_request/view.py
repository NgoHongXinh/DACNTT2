import uuid
import logging
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.friend_request.schema import ResponseFriendRequest, ResponseCreateFriendRequest, ResponseFriendOfUser
from api.library.constant import CODE_ERROR_USER_CODE_NOT_FOUND, CODE_ERROR_INPUT, \
    CODE_ERROR_WHEN_UPDATE_CREATE, CODE_ERROR_SERVER, CODE_ERROR_WHEN_UPDATE_CREATE_NOTI, \
    CODE_ERROR_WHEN_UPDATE_CREATE_FRIEND_REQUEST, CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, \
    CODE_ERROR_WHEN_UPDATE_CREATE_USER, CODE_ERROR_FRIEND_REQUEST_NOT_FOUND
from api.library.function import check_friend_or_not_in_profile
from api.third_parties.database.model.friend_request import FriendRequest
from api.third_parties.database.model.notification import Notification
from api.third_parties.database.query.friend_request import get_friend, create_fr, update_friend_request, \
    get_all_friend_request, delete_friend_request
from api.third_parties.database.query.notification import create_noti
from api.third_parties.database.query.user import get_user_by_code, update_user_friend, remove_user_friend, \
    get_list_user_in_list
from settings.init_project import open_api_standard_responses, http_exception


logger = logging.getLogger("friend_request.view.py")
router = APIRouter()


@router.get(
    path="/friend-request",
    name="get all friend request",
    description="get all friend request",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseFriendRequest]],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_friend_requests(last_user_ids: str = Query(default=""), user: dict = Depends(get_current_user)):
    try:
        list_friend_request_cursor = await get_all_friend_request(
            user_code=user['user_code'],
            last_friend_request_id=last_user_ids)
        list_friend_request_cursor = await list_friend_request_cursor.to_list(None)
        response = {
            "data": list_friend_request_cursor,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[List[ResponseFriendRequest]](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code= HTTP_500_INTERNAL_SERVER_ERROR,
            code= CODE_ERROR_SERVER,
        )


@router.post(
    path="/friend-request/{user_code_want_request}",
    name="request_new_frient",
    description="send request friend to new people",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseCreateFriendRequest],
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
            return SuccessResponse[ResponseCreateFriendRequest](**{
                "data": {"message":"Send request success"},
                "response_status": {
                    "code": CODE_SUCCESS,
                    "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
                }
            })
        else:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_FRIEND_REQUEST
            raise HTTPException(status_code)
    except:
        logger.error(message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.post(
    path="/accept-friend-request/{user_code_in_queue_request}",
    name="accept_new_friend",
    description="accept friend request",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseFriendRequest]],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def accept_friend(
        user_code_in_queue_request: str = Path(description="user code của người gửi lời mời kết bạn"),
        user: dict = Depends(get_current_user)
):
    code = message = status_code = ''
    try:
        accept_friend = await update_friend_request(user_code_in_queue_request, user['user_code'], False, True)
        if not accept_friend:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_FRIEND_REQUEST_NOT_FOUND
            raise HTTPException(status_code)
        # cập nhật lại danh sách bạn bè cho cả 2 người
        # nếu xảy ra lỗi trong quá trình cập nhật => rollback lại trạng thái trước khi cập nhật của cả 2 user
        check_exist_user = await get_user_by_code(user_code_in_queue_request)
        if not check_exist_user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            raise HTTPException(status_code)

        update_friend_for_current_user = await update_user_friend(user_code_in_queue_request, user['user_code'])
        if update_friend_for_current_user:
            update_friend_for_request_user = await update_user_friend(user['user_code'], user_code_in_queue_request)
            if not update_friend_for_request_user:
                roll_back_friend = await remove_user_friend(user_code_in_queue_request, user['user_code'])
                roll_back_friend_request = await update_friend_request(
                    user_code_in_queue_request,
                    user['user_code'],
                    True,
                    False
                )
                status_code = HTTP_400_BAD_REQUEST
                code = CODE_ERROR_WHEN_UPDATE_CREATE_USER
                raise HTTPException(status_code)
        else:
            roll_back_friend_request = await update_friend_request(
                user_code_in_queue_request,
                user['user_code'],
                True,
                False
            )
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_USER
            raise HTTPException(status_code)
        # cập nhật thành công hết thì trả lại danh sách lời mời kết bạn hiện tại
        list_friend_request_cursor = await get_all_friend_request()
        list_friend_request_cursor = await list_friend_request_cursor.to_list(None)
        response = {
                "data": list_friend_request_cursor,
                "response_status": {
                    "code": CODE_SUCCESS,
                    "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
                }
            }
        return SuccessResponse[List[ResponseFriendRequest]](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if code else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.delete(
    path="/deny-friend-request/{friend_request_code}",
    name="deny_new_friend",
    description="deny friend request",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseCreateFriendRequest],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def deny_friend(friend_request_code: str, user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        deny_friend = await delete_friend_request(friend_request_code)
        if not deny_friend:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_FRIEND_REQUEST_NOT_FOUND
            raise HTTPException(status_code)
        return SuccessResponse[ResponseCreateFriendRequest](**{
            "data": {"message": "deny request success"},
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        })
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if code else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.get(
    path="/get-all-friend/user/{user_code}",
    name="deny_new_friend",
    description="deny friend request",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseFriendOfUser]],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_all_friend_of_user(
        user_code: str,
        last_friend_id: str = Query(default="", description='id cuối cùng của user trong danh sách bạn bè '),
        user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        user_info = await get_user_by_code(user_code)
        if not user_info:
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            status_code = HTTP_400_BAD_REQUEST
            raise HTTPException(status_code)
        get_friend_of_user = await get_list_user_in_list(user_info['friends_code'], last_friend_id)
        get_friend_of_user = await get_friend_of_user.to_list(None)
        # th vào trang bạn bè của người khác
        # kiểm tra xem danh sách bạn bè của người đó có ai là bạn với mình hay đã gửi lời mời ...
        if user_code != user['user_code']:
            for index, friend in enumerate(get_friend_of_user):
                # nếu nguowfi đang onle là bạn bè của user_code đang cần tìm thì bỏ qua vì đã kiểm tra ở bên user rồi
                if user['user_code'] == friend['user_code']:
                    get_friend_of_user.pop(index)
                    break
            for index, friend in enumerate(get_friend_of_user):
                get_friend_of_user[index]['friend_status'] = await check_friend_or_not_in_profile(
                    current_user=user['user_code'],
                    user_code_check=friend['user_code'],
                    list_friend_code=user['friends_code'])
        response = {
            "data": get_friend_of_user,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[List[ResponseFriendOfUser]](**response)

    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if code else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )
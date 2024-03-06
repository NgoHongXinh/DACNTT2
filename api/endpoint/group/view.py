import uuid

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List
import logging

from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.group.schema import RequestCreateGroup, ResponseGroup, ResponseListGroup, \
    RequestUpdateUser
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_SERVER, CODE_ERROR_INPUT, \
    CODE_ERROR_USER_CODE_NOT_FOUND, CODE_ERROR_WHEN_UPDATE_CREATE_GROUP, CODE_ERROR_GROUP_CODE_NOT_FOUND


from api.third_parties.database.query.user import get_user_by_code
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
logger = logging.getLogger("conversation.view.py")


@router.post(
    path="/conversation/group",
    name="create_group",
    description="create new group",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseGroup],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_new_group(user_chat: RequestCreateGroup, user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)
        user_code_chat = user_chat.list_user_to_chat
        if not user_code_chat:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = 'list_user_to_chat not allow empty'
            raise HTTPException(status_code)

        # Kiểm tra xem user có tồn tại không bằng cách kiểm tra user_code
        for user_code in user_code_chat:
            receiver = await get_user_by_code(user_code)
            # code kiểm tra và xử lý user
            if not receiver:
                status_code = HTTP_400_BAD_REQUEST
                code = CODE_ERROR_USER_CODE_NOT_FOUND
                raise HTTPException(status_code)
        members = [user['user_code']]
        members.extend(user_code_chat)

        # Kiểm tra xem group đã tồn tại chưa nếu có thì trả về group đó
        existing_group = await get_group_by_members(members)
        if existing_group:
            existing_group_name = await get_group_by_name(user_chat.name)
            if existing_group_name:
                return SuccessResponse[ResponseGroup](**{
                    "data": existing_group_name,
                    "response_status": {
                        "code": CODE_SUCCESS,
                        "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
                    }
                })

        # Nếu group chưa tồn tại thì tạo mới
        group_data = Group(
            members=members,
            conversation_code=str(uuid.uuid4()),
            name=user_chat.name
        )
        group_id = await create_group(group_data)
        if not group_id:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_GROUP
            raise HTTPException(status_code)
        new_group = await get_group_by_id(group_id)
        response = {
            "data": new_group,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseGroup](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.post(
    path="/group/{conversation_code}/users",
    name="add_list_user_to_group",
    description="add new list user to group",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseGroup],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def add_list_users_to_group(add_user: RequestUpdateUser,
                                  conversation_code: str,
                                  user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)

        new_user_code = add_user.list_user_code
        if not new_user_code:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = 'list_new_user_code not allow empty'
            raise HTTPException(status_code)

        group = await get_group_by_code(conversation_code)
        if not group:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_GROUP_CODE_NOT_FOUND
            raise HTTPException(status_code)

        existing_members = group['members']
        duplicate_members = []

        # Kiểm tra xem các user có tồn tại không
        for user_code in add_user.list_user_code:
            user = await get_user_by_code(user_code)
            if not user:
                status_code = HTTP_400_BAD_REQUEST
                code = CODE_ERROR_USER_CODE_NOT_FOUND
                raise HTTPException(status_code)

            # Kiểm tra xem các user có trong group không
            if user_code in existing_members:
                duplicate_members.append(user_code)

            else:
                # Thêm user_code vào danh sách thành viên
                group['members'].append(user_code)

        if duplicate_members:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = f"User code = {', '.join(duplicate_members)} already exists in the group"
            raise HTTPException(status_code)

        updated_group = await add_user_to_group(group['members'], conversation_code)
        if not updated_group:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_GROUP
            raise HTTPException(status_code)

        response = {
            "data": updated_group,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseGroup](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.delete(
    path="/group/{conversation_code}/users",
    name="remove_users_from_group",
    description="Remove users from a group",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseGroup],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def remove_users_from_group(conversation_code: str, del_user: RequestUpdateUser,
                                  user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)

        del_user_code = del_user.list_user_code
        if not del_user_code:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = 'list_user_code not allow empty'
            raise HTTPException(status_code)

        group = await get_group_by_code(conversation_code)
        if not group:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_conversation_code_NOT_FOUND
            raise HTTPException(status_code)

        existing_members = group['members']
        empty_members = []

        # Kiểm tra xem các user có tồn tại không
        for user_code in del_user.list_user_code:
            user = await get_user_by_code(user_code)
            if not user:
                status_code = HTTP_400_BAD_REQUEST
                code = CODE_ERROR_USER_CODE_NOT_FOUND
                raise HTTPException(status_code)

            # Kiểm tra xem các user có trong group không
            if user_code not in existing_members:
                empty_members.append(user_code)
            else:
                group['members'].remove(user_code)

        if empty_members:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = f"User code = {', '.join(empty_members)} not exists in the group"
            raise HTTPException(status_code)

        updated_group = await del_user_from_group(conversation_code, group['members'])
        response = {
            "data": updated_group,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseGroup](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )

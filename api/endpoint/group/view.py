import uuid

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List
import logging

from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.group.schema import RequestCreateGroup, ResponseGroup, ResponseListGroup
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_SERVER, CODE_ERROR_INPUT, \
    CODE_ERROR_USER_CODE_NOT_FOUND, CODE_ERROR_WHEN_UPDATE_CREATE_GROUP, CODE_ERROR_GROUP_CODE_NOT_FOUND
from api.third_parties.database.model.group import Group
from api.third_parties.database.query.group import get_all_group_of_current_user, get_group_by_members, create_group, \
    get_group_by_code, add_user_to_group, get_group_by_id

from api.third_parties.database.query.user import get_user_by_code
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
logger = logging.getLogger("group.view.py")


@router.get(
    path="/group/user/{user_code}",
    name="get_all_groups",
    description="get all groups of current user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseListGroup],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_all_group(user: dict = Depends(get_current_user), last_user_ids: str = Query(default="")):
    code = message = status_code = ''
    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)

        list_group_cursor = await get_all_group_of_current_user(
            user_code=user['user_code'],
            last_group_id=last_user_ids
        )
        list_group_cursor = await list_group_cursor.to_list(None)

        for group in list_group_cursor:
            print(group['_id'], group['created_time'])
            list_user_to_chat = await get_user_by_code(group['members'][1:])
            user = await get_user_by_code(group['members'][0])
            group["list_user_to_chat"] = list_user_to_chat
            group["current_user_code"] = user

        last_group_id = ObjectId("                        ")
        if list_group_cursor:
            last_group = list_group_cursor[-1]
            print(last_group)
            last_group_id = last_group['_id']
            print(type(last_group_id))

        response = {
            "data":
                {
                    "list_group_info": list_group_cursor,
                    "last_group_id": last_group_id
                },
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseListGroup](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.post(
    path="/group",
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
        receiver_ids = user_chat.list_user_to_chat
        if not receiver_ids:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = 'list_user_to_chat not allow empty'
            raise HTTPException(status_code)

        # Kiểm tra xem user có tồn tại không bằng cách kiểm tra user_code
        for receiver_id in receiver_ids:
            receiver = await get_user_by_code(receiver_id)
            # code kiểm tra và xử lý user
            if not receiver:
                status_code = HTTP_400_BAD_REQUEST
                code = CODE_ERROR_USER_CODE_NOT_FOUND
                raise HTTPException(status_code)
        members = [user['user_code']]
        members.extend(receiver_ids)
        # Kiểm tra xem group đã tồn tại chưa nếu có thì trả về group đó
        existing_group = await get_group_by_members(members)
        if existing_group:
            return SuccessResponse[ResponseGroup](**{
                "data": existing_group,
                "response_status": {
                    "code": CODE_SUCCESS,
                    "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
                }
            })

        # Nếu group chưa tồn tại thì tạo mới
        group_data = Group(
            members=members,
            group_code=str(uuid.uuid4()),
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
    path="/group/{group_code}/user/{new_user_code}",
    name="add_user_to_group",
    description="add new user to group",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseGroup],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def add_new_user_to_group(group_code: str,
                                new_user_code: str,
                                user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)
        user_want_add = await get_user_by_code(new_user_code)
        if not user_want_add:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            raise HTTPException(status_code)

        group = await get_group_by_code(group_code)
        if not group:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_GROUP_CODE_NOT_FOUND
            raise HTTPException(status_code)

        if user_want_add in group['members']:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = f"user code = {user_want_add} user already in group"
            raise HTTPException(status_code)

        add_user = await add_user_to_group(new_user_code, group_code)
        print(add_user)
        if not add_user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_GROUP
            raise HTTPException(status_code)

        response = {
            "data": add_user,
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

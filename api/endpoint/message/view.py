import logging
import uuid
from typing import List
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, Query

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.message.schema import ResponseMessage, RequestCreateMessage, ResponseGroupMessage, \
    RequestCreateMessageGroup
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_SERVER, CODE_ERROR_INPUT, \
    CODE_ERROR_USER_CODE_NOT_FOUND, CODE_ERROR_CONVERSATION_CODE_NOT_FOUND, CODE_ERROR_GROUP_CODE_NOT_FOUND
from api.third_parties.database.model.message import Message, MessageGroup
from api.third_parties.database.query.conversation import get_conversation_by_code
from api.third_parties.database.query.group import get_group_by_code
from api.third_parties.database.query.message import create_message, get_message_by_message_code, \
    get_all_message_by_conversation_code, get_message_id, create_message_group
from api.third_parties.database.query.user import get_user_by_code
from api.third_parties.socket.socket import sio_server
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
logger = logging.getLogger("message.view.py")


@router.post(
    path="/message",
    name="create_message",
    description="create message",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseMessage],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_a_message(request_message_data: RequestCreateMessage,
                           user: dict = Depends(get_current_user)):
    code = message = status_code = ''

    try:
        sender_code = request_message_data.sender_code
        sender = await get_user_by_code(sender_code)
        if not sender:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            raise HTTPException(status_code)

        conversation_code = request_message_data.conversation_code
        conversation = await get_conversation_by_code(conversation_code)
        if not conversation:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_CONVERSATION_CODE_NOT_FOUND
            raise HTTPException(status_code)

        message_data = Message(
            message_code=str(uuid.uuid4()),
            conversation_code=conversation_code,
            sender_code=sender_code,
            text=request_message_data.text
        )
        new_message_id = await create_message(message_data)
        print(new_message_id)

        new_message = await get_message_id(new_message_id)
        # await sio_server.emit("receiveNewMess", new_message_id, room=new_message_id.conversation_code)

        response = {
            "data": new_message,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseMessage](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.get(
    path="/conversation/{conversation_code}/message",
    name="get_all_message",
    description="get all message by conversation_code",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseMessage]],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_all_message(conversation_code: str, last_message_id: str = Query(default="")):
    try:
        if not conversation_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='conversation_code not allow empty')
        list_mess_cursor = await get_all_message_by_conversation_code(
            conversation_code=conversation_code,
            last_message_id=last_message_id
        )
        list_mess_cursor = await list_mess_cursor.to_list(None)
        response = {
            "data": list_mess_cursor,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[List[ResponseMessage]](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.post(
    path="/message/group",
    name="create_message_group",
    description="create message in group",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseGroupMessage],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_a_message_group(request_message_group_data: RequestCreateMessageGroup,
                                 user: dict = Depends(get_current_user)):
    code = message = status_code = ''
    try:
        sender_group_code = request_message_group_data.sender_code

        sender_group = await get_user_by_code(sender_group_code)
        if not sender_group:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            raise HTTPException(status_code)

        group_code = request_message_group_data.group_code

        group = await get_group_by_code(group_code)
        if not group:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_GROUP_CODE_NOT_FOUND
            raise HTTPException(status_code)

        message_group_data = MessageGroup(
            message_code=str(uuid.uuid4()),
            group_code=group_code,
            sender_code=sender_group_code,
            text=request_message_group_data.text
        )
        new_message_group = await create_message_group(message_group_data)

        new_message_group_id = await get_message_id(new_message_group)
        # await sio_server.emit("receiveNewMess", new_message_id, room=new_message_id.conversation_code)

        response = {
            "data": new_message_group_id,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseGroupMessage](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )

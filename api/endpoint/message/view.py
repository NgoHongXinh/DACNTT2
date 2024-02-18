import logging
import uuid
from typing import List
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, Query

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.message.schema import ResponseMessage, RequestCreateMessage
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_SERVER
from api.third_parties.database.model.message import Message
from api.third_parties.database.query.conversation import get_conversation_by_code
from api.third_parties.database.query.message import create_message, get_message_by_message_code, get_all_message_by_conversation_code
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
    try:
        if not request_message_data.conversation_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='conversation_code not allow empty')

        message_data = Message(
            message_code=str(uuid.uuid4()),
            conversation_code=request_message_data.conversation_code,
            sender_code=request_message_data.sender_code,
            text=request_message_data.text
        )
        new_message = await create_message(message_data)

        new_message_obj = await get_message_by_message_code(new_message)
        response = {
            "data": ResponseMessage.parse_obj(new_message_obj.to_json()),
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseMessage](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
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
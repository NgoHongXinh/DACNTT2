import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List
import logging

from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.conversation.schema import ResponseConversation, RequestCreateConversation
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_SERVER, CODE_ERROR_INPUT, \
    CODE_ERROR_USER_CODE_NOT_FOUND
from api.third_parties.database.model.conversation import Conversation
from api.third_parties.database.query.conversation import get_conversation_by_code, \
    get_all_conversation_of_current_user, create_conversation, get_conversation_by_members
from api.third_parties.database.query.friend_request import get_friend
from api.third_parties.database.query.user import get_user_by_code
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
logger = logging.getLogger("conversation.view.py")


@router.get(
    path="/conversation",
    name="get_conversation",
    description="get a conversation of current user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseConversation],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_conversation(conversation_code: str):
    if not conversation_code:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='conversation_code not allow empty')
    cursor = await get_conversation_by_code(conversation_code)
    print(cursor)
    response = {
        "data": cursor,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseConversation](**response)


@router.get(
    path="/conversation/user/{user_code}",
    name="get_all_conversations",
    description="get all conversations of current user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseConversation]],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_all_conversation(user: dict = Depends(get_current_user), last_user_ids: str = Query(default="")):
    try:
        list_conversation_cursor = await get_all_conversation_of_current_user(
            user_code=user['user_code'],
            last_conversation_id=last_user_ids
        )
        list_conversation_cursor = await list_conversation_cursor.to_list(None)

        response = {
            "data": list_conversation_cursor,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[List[ResponseConversation]](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.post(
    path="/conversation",
    name="create_conversation",
    description="create conversation",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseConversation],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_new_conversation(user_chat: RequestCreateConversation,
                                  user: dict = Depends(get_current_user)):
    try:
        receiver_id = user_chat.user_code_to_chat

        # Kiểm tra xem user có tồn tại không bằng cách kiểm tra user_code
        receiver = await get_user_by_code(receiver_id)

        if not receiver:
            return http_exception(
                status_code=HTTP_400_BAD_REQUEST,
                message=f"User with user_code {receiver_id} does not exist."
            )

        # Kiểm tra xem conversation đã tồn tại chưa nếu có thì trả về conversation đó
        existing_conversation = await get_conversation_by_members([user['user_code'], receiver_id])
        if existing_conversation:
            return SuccessResponse[ResponseConversation](**{
                "data": existing_conversation,
                "response_status": {
                    "code": CODE_SUCCESS,
                    "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
                }
            })

        # Nếu conversation chưa tồn tại thì tạo mới
        conversation_data = Conversation(
            members=[user['user_code'], receiver_id],  # 2 người tham gia cuộc trò chuyện
            conversation_code=str(uuid.uuid4())
        )
        conversation = await create_conversation(conversation_data)
        response = {
            "data": conversation,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseConversation](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


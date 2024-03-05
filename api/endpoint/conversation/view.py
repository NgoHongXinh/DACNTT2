import uuid

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List
import logging

from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.conversation.schema import ResponseConversation, RequestCreateConversation, ResponseListConversation, \
    ResponseCreateConversation
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_SERVER, CODE_ERROR_INPUT, \
    CODE_ERROR_USER_CODE_NOT_FOUND, CODE_ERROR_WHEN_UPDATE_CREATE_CONVERSATION
from api.library.function import get_max_stt_and_caculate_in_convertsation
from api.third_parties.database.model.conversation import Conversation
from api.third_parties.database.query.conversation import get_conversation_by_code, \
    get_all_conversation_of_current_user, create_conversation, get_conversation_by_members
from api.third_parties.database.query.user import get_user_by_code, get_list_user_by_code
from api.third_parties.database.query.user_online import get_user_if_user_is_online
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
    status_code = code = message = ""

    try:
        if not conversation_code:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = 'conversation_code not allow empty'
            raise HTTPException(status_code)
        cursor = await get_conversation_by_code(conversation_code)
        response = {
            "data": cursor,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }

        return SuccessResponse[ResponseConversation](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.get(
    path="/conversations",
    name="get_all_conversations",
    description="get all conversations of current user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseListConversation],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_all_conversation(user: dict = Depends(get_current_user), last_conversation_ids: str = Query(default="")):
    code = message = status_code = ''
    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)

        list_conversation_cursor = await get_all_conversation_of_current_user(
            user_code=user['user_code'],
            last_conversation_id=last_conversation_ids
        )
        list_conversation_cursor = await list_conversation_cursor.to_list(None)

        for conversation in list_conversation_cursor:
            members = conversation['members']
            conversation['members_obj'] =[]
            conversation['online'] = False
            for member in members:
                print(member)
                if member != user['user_code']:
                    user_member = await get_user_by_code(member)
                    get_other_user_if_online = await get_user_if_user_is_online(member)
                    print("vaof", member, get_other_user_if_online)
                    if get_other_user_if_online:
                        conversation['online'] = True
                    conversation['members_obj'].append(user_member)


        last_conversation_id = ObjectId("                        ")
        if list_conversation_cursor:
            last_conversation = list_conversation_cursor[-1]
            last_conversation_id = last_conversation['_id']

        response = {
            "data":
                {
                    "list_conversation_info": list_conversation_cursor,
                    "last_conversation_id": last_conversation_id
                },
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseListConversation](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )


@router.post(
    path="/conversation",
    name="create_conversation",
    description="create conversation",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseCreateConversation],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_new_conversation(user_chat: RequestCreateConversation,
                                  user: dict = Depends(get_current_user)):
    code = message = status_code = ''

    try:
        if not user:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = "user not allow empty"
            raise HTTPException(status_code)
        user_code_chat = user_chat.user_code_to_chat
        if not user_code_chat:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_INPUT
            message = 'user_code_to_chat not allow empty'
            raise HTTPException(status_code)

        # Kiểm tra xem user có tồn tại không bằng cách kiểm tra user_code
        receiver = await get_user_by_code(user_code_chat)
        if not receiver:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_USER_CODE_NOT_FOUND
            raise HTTPException(status_code)

        # Kiểm tra xem conversation đã tồn tại chưa nếu có thì trả về conversation đó
        existing_conversation = await get_conversation_by_members([user['user_code'], user_code_chat])
        if existing_conversation:
            return SuccessResponse[ResponseConversation](**{
                "data": existing_conversation,
                "response_status": {
                    "code": CODE_SUCCESS,
                    "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
                }
            })

        # Nếu conversation chưa tồn tại thì tạo mới
        max_stt = await get_max_stt_and_caculate_in_convertsation(user['user_code'])
        conversation_data = Conversation(
            members=[user['user_code'], user_code_chat],  # 2 người tham gia cuộc trò chuyện
            conversation_code=str(uuid.uuid4()),
            stt=max_stt
        )
        conversation = await create_conversation(conversation_data)
        if not conversation:
            status_code = HTTP_400_BAD_REQUEST
            code = CODE_ERROR_WHEN_UPDATE_CREATE_CONVERSATION
            raise HTTPException(status_code)

        response = {
            "data": {"message": "success"},
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }

        return SuccessResponse[ResponseCreateConversation](**response)
    except:
        logger.error(TYPE_MESSAGE_RESPONSE["en"][code] if not message else message, exc_info=True)
        return http_exception(
            status_code=status_code if status_code else HTTP_500_INTERNAL_SERVER_ERROR,
            code=code if code else CODE_ERROR_SERVER,
            message=message
        )



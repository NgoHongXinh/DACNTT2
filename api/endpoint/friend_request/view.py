from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.friend_request.schema import ResponseFriendRequest
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE
from api.third_parties.database.query.friend_request import get_friend_request_id
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
@router.get(
    path="/friend_request",
    name="123",
    description="",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseFriendRequest],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_friend_request(friend_request_id: str):
    if not friend_request_id:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='friend_request_id not allow empty')
    cursor = await get_friend_request_id(friend_request_id)
    print(cursor)
    response = {
        "data": cursor,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseFriendRequest](**response)


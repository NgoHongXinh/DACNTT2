from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.user_online.schema import ResponseUserOnline
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE
from api.third_parties.database.query.user_online import get_user_online_id
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
@router.get(
    path="/user_online",
    name="123",
    description="",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseUserOnline],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_user_online(user_online_id: str):
    if not user_online_id:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='user_online_id not allow empty')
    cursor = await get_user_online_id(user_online_id)
    print(cursor)
    response = {
        "data": cursor,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseUserOnline](**response)


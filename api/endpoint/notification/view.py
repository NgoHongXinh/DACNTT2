from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.notification.schema import ResponseNotification
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE
from api.third_parties.database.query.notification import get_notification_id
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
@router.get(
    path="/notification",
    name="123",
    description="",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseNotification],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_notification(notification_id: str):
    if not notification_id:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='notification_id not allow empty')
    cursor = await get_notification_id(notification_id)
    print(cursor)
    response = {
        "data": cursor,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseNotification](**response)



import logging

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.notification.schema import ResponseNotification, ResponseListNotification, ResponseNumberNotification
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND, \
    CODE_ERROR_SERVER, CODE_ERROR_INPUT
from api.third_parties.database.query import notification as query_notification
from api.third_parties.database.query.user import get_user_by_code
from settings.init_project import open_api_standard_responses, http_exception
from api.base.authorization import get_current_user

logger = logging.getLogger("notification.view.py")
router = APIRouter()


@router.get(
    path="/notification",
    name="get_all_notification",
    description="get all notification",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseListNotification],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_notification(user: dict = Depends(get_current_user), last_notification_id: str = Query(default="")):
    try:
        if not user:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='user not allow empty')
        notifications = await query_notification.get_notifications(
            user_code=user['user_code'],
            last_notification_id=last_notification_id
        )
        if not notifications:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND)
        list_notifications_cursor = await notifications.to_list(None)
        print(list_notifications_cursor)

        for noti in list_notifications_cursor:
            user_guest = await get_user_by_code(noti['user_code_guest'])
            noti["user_info"] = user
            noti["user_guest_info"] = user_guest

        response = {
            "data": {
                "list_noti_info": list_notifications_cursor

            },
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        print(response)
        return SuccessResponse[ResponseListNotification](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.delete(
    path="/notifications/{notification_code}",
    name="delete_notification",
    description="delete a notification",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseNotification],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def delete_notification(notification_code: str, user: dict = Depends(get_current_user)):
    try:
        if not notification_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND)
        deleted = await query_notification.delete_notification(
            notification_code,
            user['user_code']
        )
        if not deleted:
            return {"message": "Failed notification delete"}

        return deleted
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.put(
    path="/notifications/{notification_code}",
    name="update_notification",
    description="update a notification",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseNotification],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def update_notification(notification_code: str, user: dict = Depends(get_current_user)):
    try:
        updated = await query_notification.update_notification(
            notification_code,
            user['user_code']
        )
        if not updated:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND)
        response = {
            "data": updated,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }

        return SuccessResponse[ResponseNotification](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )

@router.get(
    path="/number-notification",
    name="get_number_notification",
    description="get all number of notification which user not read",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseNumberNotification],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_number_notification(user: dict = Depends(get_current_user)):
    try:
        if not user:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='user not allow empty')
        notifications = await query_notification.get_noti_not_read(user_code=user['user_code'])
        list_notifications_cursor = await notifications.to_list(None)
        count = 0

        for noti in list_notifications_cursor:
            if noti['is_checked'] is False:
                count += 1

        response = {
            "data": {
                "number_noti_not_read": str(count)

            },
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        return SuccessResponse[ResponseNumberNotification](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )

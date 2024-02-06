import uuid
import logging

from typing import List
from fastapi import APIRouter, Depends, Form, Query
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.notification.schema import ResponseNotification, ResponseDeleteNotification
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND, CODE_ERROR_SERVER
from api.third_parties.database.model.notification import Notification
from api.third_parties.database.query import notification as query_notification
from settings.init_project import open_api_standard_responses, http_exception
from api.base.authorization import get_current_user

logger = logging.getLogger("notification.view.py")
router = APIRouter()


@router.get(
    path="/notification/user_code/{user_code}",
    name="get_all_notifications",
    description="get all notifications",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseNotification]],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_all_notifications_by_user(user: dict = Depends(get_current_user), last_notification_id: str = Query(default="")):
    try:
        if not user:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='user not allow empty')
        list_notifications_cursor = await query_notification.get_all_notifications(
            user_code=user['user_code'],
            last_notification_id=last_notification_id
        )
        if not list_notifications_cursor:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND)
        list_notifications_cursor = await list_notifications_cursor.to_list(None)
        print(list_notifications_cursor)
        response = {
            "data": list_notifications_cursor,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }

        return SuccessResponse[List[ResponseNotification]](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )

@router.get(
    path="/notification/{notification_code}",
    name="get_notification",
    description="get a notification",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseNotification],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_notification(notification_code: str):
    try:
        if not notification_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='notification_code not allow empty')
        notification = await query_notification.get_notification_by_notification_code(notification_code)

        response = {
            "data": notification,
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


@router.delete(
    path="/notifications/{notification_code}",
    name="delete_notification",
    description="delete a notification",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseDeleteNotification],
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
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='Failed notification delete')

        return SuccessResponse[ResponseDeleteNotification](**{
            "data": {"message": "thông báo đã được ẩn đi"},
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        })
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
        if not notification_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_NOTIFICATION_CODE_NOT_FOUND)
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
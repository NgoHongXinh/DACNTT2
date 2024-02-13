import datetime
from typing import List

from pydantic import BaseModel,  Field

from api.endpoint.user.schema import ResponseUser


class ResponseNotification(BaseModel):
    notification_code: str = Field("", example='')
    user_code: str = Field("", example='')
    user_code_guest: str = Field("", example='')
    content: str = Field("", example='')
    is_checked: bool = Field("", example=False)
    deleted_flag: bool = Field("", example=False)


class ResponseNotificationInfo(BaseModel):
    notification_code: str = Field("", example='')
    user_info: ResponseUser
    user_guest_info: ResponseUser
    content: str = Field("", example='')
    is_checked: bool = Field("", example=False)
    deleted_flag: bool = Field("", example=False)
    created_time: datetime.datetime


class ResponseListNotification(BaseModel):
    number_noti_not_read: str = Field("0")
    list_noti_info: List[ResponseNotificationInfo] = Field(...)

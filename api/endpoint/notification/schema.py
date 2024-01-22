from pydantic import BaseModel,  Field

# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseNotification(BaseModel):
    notification_code: str = Field("", example='')
    user_code: str = Field("", example='')
    user_code_guest: str = Field("", example='')
    content: str = Field("", example='')
    is_checked: bool = Field("", example=False)
    deleted_flag: bool = Field("", example=False)



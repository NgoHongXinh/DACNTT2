from typing import List

from fastapi import APIRouter, Depends, Form, UploadFile, Query
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.user.schema import ResponseUser, ResponseUserProfile

from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_USER_CODE_NOT_FOUND, \
    CODE_ERROR_CANT_CHANGE_INFO, CODE_ERROR_WHEN_UPDATE_CREATE
from api.third_parties.cloud.query import upload_image_cloud
from api.third_parties.database.query.user import get_user_by_code, regex_user_name_email, update_user

from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()


@router.get(
    path="/user/find-user",
    name="find_user",
    description="find user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseUserProfile]],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def find_friend(name_or_email: str = Query(default=""), user: dict = Depends(get_current_user)):

    data = None
    if name_or_email:
        data = await regex_user_name_email(name_or_email)

    response = {
        'data': data,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    return SuccessResponse[List[ResponseUserProfile]](**response)


@router.get(
    path="/user/{user_code}",
    name="123",
    description="",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseUser],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_user_login(user_code: str, user: dict = Depends(get_current_user)):
    if not user_code:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='user_code not allow empty')
    if user_code == user['user_code']:
        response = {
            "data": user,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
    }
    else:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_USER_CODE_NOT_FOUND)

    return SuccessResponse[ResponseUser](**response)


@router.get(
    path="/user/profile/{user_code}",
    name="get_profile_user",
    description="get profile user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseUserProfile],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_user_profile(user_code: str, user: dict = Depends(get_current_user)):
    if not user_code:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='user_code not allow empty')
    profile = await get_user_by_code(user_code)
    if not profile:
        return http_exception(status_code=HTTP_400_BAD_REQUEST,
                              code=CODE_ERROR_USER_CODE_NOT_FOUND)
    if user_code == user['user_code']:
        profile['is_current_login_user'] = True
    else:
        profile['is_current_login_user'] = False
    print(profile)
    # cần làm thêm trang cá nhân của người đó có được gửi yêu cầu kết bạn hay không
    return SuccessResponse[ResponseUserProfile](**{
        "data": profile,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
    })


@router.post(
    path="/user/{user_code}",
    name="get_profile_user",
    description="get profile user",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseUser],
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def update_user_info(
        user_code: str,
        given_name: str = Form(None),
        family_name: str = Form(None),
        biography: str = Form(None),
        faculty: str = Form(None),
        birthday: str = Form(None),
        phone: str = Form(None),
        gender: str = Form(None),
        class_name: str = Form(None),
        picture: UploadFile = Form(None),
        background_picture: UploadFile = Form(None),
        user: dict = Depends(get_current_user)):
    if user_code != user['user_code']:
        return http_exception(status_code=HTTP_400_BAD_REQUEST,
                              code=CODE_ERROR_CANT_CHANGE_INFO)
    data_update = {

    }
    if given_name is not None:
        data_update['given_name'] = given_name
    if family_name is not None:
        data_update['family_name'] = family_name
    if biography is not None:
        data_update['biography'] = biography
    if faculty is not None:
        data_update['faculty'] = faculty
    if birthday is not None:
        data_update['birthday'] = birthday
    if phone is not None:
        data_update['phone'] = phone
    if gender is not None:
        data_update['gender'] = gender
    if class_name is not None:
        data_update['class_name'] = class_name
    user_after_update = await update_user(user['_id'], data_update)
    await upload_image_cloud(await picture.read(), user["user_code"])
    if not user_after_update:
        return http_exception(code=CODE_ERROR_WHEN_UPDATE_CREATE,status_code=HTTP_400_BAD_REQUEST)

    return SuccessResponse[ResponseUser](**{
        "data": user_after_update,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    })


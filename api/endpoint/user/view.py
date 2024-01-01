from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.user.schema import ResponseUser, ResponseUserProfile
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_USER_CODE_NOT_FOUND
from api.third_parties.database.query.user import get_user_id, get_user_by_code
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()
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


import uuid

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.authorization import get_current_user, create_access_token
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.authen.schema import ResponseToken, RequestInfoToken
from api.endpoint.user.schema import ResponseUser
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_LOGIN_FAIL, EMAIL_LOGIN_FAIL
from api.third_parties.database.model.user import User
from api.third_parties.database.query.user import get_user_by_code, check_user, get_user_by_email, create_new_user, \
    get_user_id
from settings.init_project import open_api_standard_responses, http_exception, config_system
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()


@router.get(
    path="/get-token",
    name="get_login_token",
    description="get token for login system",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=ResponseToken,
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_token(user: OAuth2PasswordRequestForm = Depends()):
    username = user.username  # email
    password = user.password  # password
    user_login = await check_user(username, password)
    print(user_login)
    if not user_login:
        return http_exception(
            status_code=401,
            code=CODE_LOGIN_FAIL
        )
    token = await create_access_token(user_login['user_code'])

    return ResponseToken(
        **{"access_token": token,
           "user_info": user_login}
    )


@router.post(
    path="/oauthen-google",
    name="login_google",
    description="gettoken when login by google",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=ResponseToken,
        fail_response_model=FailResponse[ResponseStatus]
    )

)
async def get_token_google(info_token: RequestInfoToken):
    token = ''
    id_info = id_token.verify_oauth2_token(info_token.credential, requests.Request(), info_token.client_id)
    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        return http_exception(
            status_code=401,
            code=CODE_LOGIN_FAIL
        )
    # Kiểm tra email có phải email sinh viên không
    if id_info['email'].endswith("@student.tdtu.edu.vn"):
        # Kiểm tra user có tồn tại chưa
        user = await get_user_by_email(id_info['email'])
        if not user:
            # Tạo user mới nếu chưa có
            new_user_data = User(
                user_code=str(uuid.uuid4()),
                fullname=id_info['name'],
                picture=id_info['picture'],
                background_picture="",
                picture_id="",
                given_name=id_info['given_name'],
                family_name=id_info['family_name'],
                username=id_info['email'],
                biography="",
                class_name="",
                faculty="",
                friends_code=[],
                birthday="",
                phone=""
            )
            new_user = await create_new_user(new_user_data)
            user = await get_user_id(new_user)
            access_token = await create_access_token(user['user_code'])
            print("token: " + access_token)
            return ResponseToken(
                **{"access_token": access_token,
                   "user_info": user}
            )

        # Tạo JWT token
        access_token = await create_access_token(user['user_code'])
        print("token: " + access_token)
        return ResponseToken(
            **{"access_token": access_token,
               "user_info": user}
        )

    else:
        return http_exception(
            message="Email not allow",
            status_code=401,
            code=EMAIL_LOGIN_FAIL
        )





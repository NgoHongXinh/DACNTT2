from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.authorization import get_current_user, create_access_token
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.authen.schema import ResponseToken, RequestInfoToken
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_LOGIN_FAIL
from api.third_parties.database.query.user import get_user_id, check_user
from settings.init_project import open_api_standard_responses, http_exception, config_system
from google.oauth2 import id_token
from google.auth.transport import requests
router = APIRouter()


@router.post(
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

    if not user_login:
        return http_exception(
            status_code=401,
            code=CODE_LOGIN_FAIL
        )
    token = await create_access_token(user_login['user_code'])
    return ResponseToken(**{"access_token": token})




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
    # print(info_token)
    token = ''
    idinfo = id_token.verify_oauth2_token(info_token.credential, requests.Request(), info_token.client_id)
    # print(idinfo)
    return ResponseToken(**{"access_token": token})
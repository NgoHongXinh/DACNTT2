from typing import List
from fastapi import APIRouter, Depends, Form
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.comment.schema import ResponseComment, ResponseCreateUpdateComment
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_COMMENT_CODE_NOT_FOUND
from api.third_parties.database.query import comment as comment_query
from settings.init_project import open_api_standard_responses, http_exception
from api.third_parties.database.model.comment import Comment

router = APIRouter()


@router.get(
    path="/comment/{comment_code}",
    name="get_comment",
    description="get content of a comment",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseComment],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_comment(comment_code):
    if not comment_code:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='comment_code not allow empty')
    comment = await comment_query.get_comment_by_comment_code(comment_code)
    if not comment:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_COMMENT_CODE_NOT_FOUND)

    print(comment)
    response = {
        "data": comment,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseComment](**response)


@router.post(
    path="/comment",
    name="create_comment",
    description="create comment",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_201_CREATED,
        success_response_model=SuccessResponse[ResponseCreateUpdateComment],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_comment(
    content: str = Form(None),
    user: dict = Depends(get_current_user)
):
    if not content:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='content not allow empty')

    comment_data = Comment(
        content=content,
        created_by=user['user_code']
    )
    new_comment = await comment_query.create_comment(comment_data)
    comment_id = await comment_query.get_comment_by_id(new_comment)
    print(content)

    response = {
        "data": comment_id,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseCreateUpdateComment](**response)


@router.delete(
    path="/comment/{comment_code}",
    name="delete_comment",
    description="delete comment",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_201_CREATED,
        success_response_model=None,
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def delete_comment(comment_code: str):
    if not comment_code:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='comment_code not allow empty')

    comment = await comment_query.delete_comment(comment_code)
    if not comment:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_COMMENT_CODE_NOT_FOUND)

    response = {
        "data": comment,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    return None

@router.put(
    path="/comment/{comment_code}",
    name="update_comment",
    description="update comment",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_201_CREATED,
        success_response_model=SuccessResponse[ResponseCreateUpdateComment],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def update_comment(
        comment_code: str,
        content: str = Form(""),
        user: dict = Depends(get_current_user)

):
    if not comment_code and not content:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='comment_code and content not allow empty')

    comment_update = await comment_query.get_comment_by_comment_code(comment_code)
    if not comment_update:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_COMMENT_CODE_NOT_FOUND)

    comment_data = Comment(
        content=content,
        created_by=user['user_code']
    )

    new_comment = await comment_query.update_comment(comment_code, comment_data)
    comment_id = await comment_query.get_comment_by_id(new_comment)
    print(comment_id)

    response = {
        "data": comment_id,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return SuccessResponse[ResponseCreateUpdateComment](**response)
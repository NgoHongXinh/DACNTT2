from typing import List

from fastapi import APIRouter, UploadFile, File, Request, Depends
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.user.schema import ResponseUser
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE
from api.third_parties.database.query.user import get_user_id
from api.base.schema import SuccessResponse, FailResponse
from api.third_parties.database.query.user import get_user_id
from api.third_parties.database.query.post import get_post_by_user_code
from api.third_parties.database.query.comment import get_comment_id
from api.endpoint.post.schema import ResponsePost
from api.third_parties.database.query import post as post_query
from api.third_parties.database.query import user as user_query
from api.third_parties.database.query import comment as comment_query
from settings.init_project import open_api_standard_responses, http_exception

import asyncio

router = APIRouter()


@router.get(
        path="/posts",
        name="get_all_post",
        description="get all post of user ",
        status_code=HTTP_200_OK,
        responses=open_api_standard_responses(
            success_status_code=HTTP_200_OK,
            success_response_model=SuccessResponse[List[ResponsePost]],
            fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_posts(user: dict = Depends(get_current_user)):
    print(user)
    posts = await get_post_by_user_code(user['user_code'])
    print(posts)
    for post in posts:
        post['is_liked'] = False
        if user['user_code'] in post['liked_by']:  # kiểm tra chủ bài dăng đã like hay chưa
            post['is_liked'] = True

    response = {
        "data": posts,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    print(response)
    return SuccessResponse[List[ResponsePost]](**response)

# @router.get(
#     path="/{user_id}",
#     name="get_user_posts",
#     description="",
#     status_code=HTTP_200_OK,
#     responses=open_api_standard_responses(
#         success_status_code=HTTP_200_OK,
#         success_response_model=SuccessResponse[ResponsePost],
#         fail_response_model=FailResponse[ResponseStatus]
#     )
# )
# async def get_user_posts(request, user_id: str):
#     posts = await post_query.get_posts_by_user(user_id)
#
#
#     for post in posts:
#         post['is_liked'] = False
#         if request.user_id in post['liked_by']:
#             post['is_liked'] = True
#
#     return SuccessResponse(data=posts)
#
#
# @router.get(
#     path="/friends",
#     responses=open_api_standard_responses(
#         success_status_code=HTTP_200_OK,
#         success_response_model=SuccessResponse[List[ResponsePost]],
#     )
# )
# async def get_friends_posts(request, page_num: int = 0):
#     user = await user_query.get_user(request.user_id)
#
#     posts = await post_query.get_posts_by_user_ids(user.friends + [user.id], limit=10, skip=page_num * 10)
#
#     for post in posts:
#         post['is_liked'] = False
#         if request.user_id in post['liked_by']:
#             post['is_liked'] = True
#
#     return SuccessResponse(data=posts)


# @router.get(
#     path="/post/{post_id}",
#     name="get_post_id",
#     description="",
#     status_code=HTTP_200_OK,
#     responses=open_api_standard_responses(
#         success_status_code=HTTP_200_OK,
#         success_response_model=SuccessResponse[ResponsePost],
#         fail_response_model=FailResponse[ResponseStatus]
#     )
# )
# async def get_post(request, post_id: str):
#     post = await get_post_id(post_id)
#
#     if not post:
#         return http_exception(status_code=HTTP_400_BAD_REQUEST, message='post_id not allow empty')
#
#     post['is_liked'] = False
#     if request.user_id in post['liked_by']:
#         post['is_liked'] = True
#
#     response = {
#         "data": post,
#         "response_status": {
#             "code": CODE_SUCCESS,
#             "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
#         }
#     }
#
#     return SuccessResponse[ResponsePost](**response)
#
#
# @router.post(
#     path="/post",
#     name="post",
#     description="",
#     status_code=HTTP_200_OK,
#     responses=open_api_standard_responses(
#         success_status_code=HTTP_200_OK,
#         success_response_model=SuccessResponse[ResponsePost],
#         fail_response_model=FailResponse[ResponseStatus]
#     )
# )
# async def create_post(request, content: str, images: [UploadFile] = File([]), video: str = None):
#     post = await get_post_id(
#         user_id=request.user_id,
#         content=content,
#         images=[image.filename for image in images],
#         video=video
#     )
#
#     response = {
#         "data": post,
#         "response_status": {
#             "code": CODE_SUCCESS,
#             "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
#         }
#     }
#
#     return SuccessResponse[ResponsePost](**response)
#
#
# @router.put(
#     path="/{post_id}",
#     description="",
#     status_code=HTTP_200_OK,
#     responses=open_api_standard_responses(
#         success_status_code=HTTP_200_OK,
#         success_response_model=SuccessResponse[ResponsePost],
#         fail_response_model=FailResponse[ResponseStatus]
#     )
# )
# async def update_post(request, post_id: str, content: str = None, images: [UploadFile] = File([]),
#                       video: str = None):
#     post = await get_post_id(
#         post_id=post_id,
#         user_id=request.user_id,
#         content=content,
#         images=[image.filename for image in images],
#         video=video
#     )
#
#     if not post:
#         return http_exception(status_code=HTTP_400_BAD_REQUEST, message='post_id not allow empty')
#     response = {
#         "data": post,
#         "response_status": {
#             "code": CODE_SUCCESS,
#             "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
#         }
#     }
#
#     return SuccessResponse[ResponsePost](**response)
#
#
# @router.delete(
#     path="/{post_id}",
#     description="",
#     status_code=HTTP_200_OK,
#     responses=open_api_standard_responses(
#         success_status_code=HTTP_200_OK,
#         success_response_model=SuccessResponse[ResponsePost],
#         fail_response_model=FailResponse[ResponseStatus]
#     )
# )
# async def delete_post(request, post_id: str):
#     deleted = await post_query.delete_post(post_id, request.user_id)
#
#     if not deleted:
#         return http_exception(status_code=HTTP_400_BAD_REQUEST, message='post_id not allow empty')
#
#     await comment_query.delete_comments(post_id)
#
#     response = {
#         "data": deleted,
#         "response_status": {
#             "code": CODE_SUCCESS,
#             "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
#         }
#     }
#     return SuccessResponse[ResponsePost](**response)
# #

from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, Form
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from api.base.authorization import get_current_user
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_POST_CODE_NOT_FOUND
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.post.schema import ResponsePost, ResponseCreateUpdatePost
from api.third_parties.database.query import post as post_query
from api.third_parties.database.query import user as user_query
from api.third_parties.database.query import comment as comment_query
from api.third_parties.database.query.post import get_post_by_id
from settings.init_project import open_api_standard_responses, http_exception

router = APIRouter()


@router.get(
    path=f"/posts",
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
    posts = await post_query.get_all_post_by_user_code(user['user_code'])
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


@router.get(
    path="/post/{post_code}",
    name="get_post",
    description="get information of a post",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponsePost],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_post(post_code):
    post = await post_query.get_post_by_post_code(post_code)
    if not post:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_POST_CODE_NOT_FOUND)

    response = {
        "data": post,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    return SuccessResponse[ResponsePost](**response)


@router.post(
    path="/post",
    name="create_post",
    description="create post",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_201_CREATED,
        success_response_model=SuccessResponse[ResponseCreateUpdatePost],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_post(
        content: str = Form(""),
        image: List[UploadFile] = UploadFile(None),
        video: UploadFile = File(None),
        user: dict = Depends(get_current_user)
):
    # print(await image[0].read())
    print(image, content)

    if not content and not image and not video:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='content, image, video not allow empty')
    # image_urls = []
    # if image:
    #     for image_file in image:
    #         # upload_result = await get_upload(image_file.file) # upload image to cloudinary
    #         # image_urls.append(upload_result['url'])
    # else:
    #     return None
    #
    # video_url = None
    # if video:
    #     # upload_result = await get_upload(video.file)
    #     # video_url = upload_result['url']
    #     # video_url = get_link_youtube(video_url)
    #     # get link youtube
    # else:
    #     return None
    # return None

    new_post = await post_query.create_post(user['user_code'], content, image, video)
    post_id = await get_post_by_id(new_post)
    response = {
        "data": post_id,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    print(response)

    return SuccessResponse[ResponseCreateUpdatePost](**response)

@router.delete(
    path="/post/{post_code}",
    name="delete_post",
    description="delete post",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=None,
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def delete_post(post_code: str):
    post = await post_query.delete_post(post_code)

    if not post:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_POST_CODE_NOT_FOUND)
    response = {
        "data": post,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }

    return None

@router.put(
    path="/post/{post_code}",
    name="update_post",
    description="update post",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[ResponseCreateUpdatePost],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def update_post(
        post_code: str,
        content: str = Form(""),
        image: List[UploadFile] = UploadFile(None),
        video: UploadFile = File(None),
        user: dict = Depends(get_current_user)

):
    if not content and not image and not video:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='content, image, video not allow empty')
    # image_urls = []
    # if image:
    #     for image_file in image:
    #         upload_result = await get_upload(image_file.file) # upload image to cloudinary
    #         image_urls.append(upload_result['url'])
    # else:
    #     return None
    #
    # video_url = None
    # if video:
    #     upload_result = await get_upload(video.file)
    #     video_url = upload_result['url']
    #     video_url = get_link_youtube(video_url)
    #     # get link youtube
    # else:
    #     return None
    print(image, content)
    post_update = await post_query.update_post(user['user_code'], post_code, content, image, video)
    post_id = await get_post_by_id(post_update)
    response = {
        "data": post_id,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    return SuccessResponse[ResponseCreateUpdatePost](**response)




from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, Form
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from api.base.authorization import get_current_user
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_POST_CODE_NOT_FOUND, CODE_ERROR_INPUT
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.post.schema import ResponsePost, ResponseCreateUpdatePost
from api.third_parties.cloud.query import upload_image_cloud, delete_image
from api.third_parties.database.model.post import Post
from api.third_parties.database.query import post as post_query
from api.third_parties.database.query import user as user_query
from api.third_parties.database.query import comment as comment_query
from api.third_parties.database.query.post import get_post_by_id, get_post_by_post_code
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
        images_upload: List[UploadFile] = File(None),
        video_upload: UploadFile = File(None),
        user: dict = Depends(get_current_user)
):
    if not content and not images_upload and not video_upload:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='content, image, video not allow empty')
    if images_upload and len(images_upload) > 4:
        return http_exception(status_code=HTTP_400_BAD_REQUEST,
                              code=CODE_ERROR_INPUT,
                              message='Maximum image number is 4')

    image_ids =[]
    video_ids =[]
    videos =[]
    images =[]

    if images_upload:
        for image in images_upload:
            data_image_byte = await image.read()
            info_image_upload = await upload_image_cloud(data_image_byte, user['user_code'])
            image_ids.append(info_image_upload['public_id'])
            images.append(info_image_upload['url'])

    if video_upload:
        data_video_byte = await video_upload.read()
        info_video_upload = await upload_image_cloud(data_video_byte, user['user_code'])
        video_ids.append(info_video_upload['public_id'])
        videos.append(info_video_upload['url'])

    post_data = Post(
        content=content,
        image_ids=image_ids,
        images=images,
        video_ids=video_ids,
        videos=videos,
        created_by=user['user_code']
    )

    new_post = await post_query.create_post(post_data)
    post_id = await get_post_by_id(new_post)
    response = {
        "data": post_id,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
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
        images_upload: List[UploadFile] = File(None),
        video_upload: UploadFile = File(None),
        user: dict = Depends(get_current_user)

):
    if not content and not images_upload and not video_upload:
        return http_exception(status_code=HTTP_400_BAD_REQUEST, message='content, image, video not allow empty')
    image_ids =[]
    video_ids =[]
    videos =[]
    images =[]


    post_need_update = await get_post_by_post_code(post_code)
    if not post_need_update:
        return http_exception(HTTP_400_BAD_REQUEST, CODE_ERROR_POST_CODE_NOT_FOUND)
    list_image_need_delete_incloud = post_need_update['image_ids']
    list_video_need_delete_incloud = post_need_update['video_ids']
    if images_upload:
        for image in images_upload:
            data_image_byte = await image.read()
            info_image_upload = await upload_image_cloud(data_image_byte, user['user_code'])
            image_ids.append(info_image_upload['public_id'])
            images.append(info_image_upload['url'])
        for image_id in list_image_need_delete_incloud:
            print(image_id)
            print(await delete_image(image_id))
    else:
        image_ids = post_need_update['image_ids']
        images = post_need_update['images']

    if video_upload:
        data_video_byte = await video_upload.read()
        info_video_upload = await upload_image_cloud(data_video_byte, user['user_code'])
        video_ids.append(info_video_upload['public_id'])
        videos.append(info_video_upload['url'])

    post_data = Post(
        content=content,
        image_ids=image_ids,
        images=images,
        video_ids=video_ids,
        videos=videos,
        created_by=user['user_code']
    )
    post_update = await post_query.update_post(post_code, post_data)

    post_id = await get_post_by_id(post_update)
    response = {
        "data": post_id,
        "response_status": {
            "code": CODE_SUCCESS,
            "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
        }
    }
    return SuccessResponse[ResponseCreateUpdatePost](**response)




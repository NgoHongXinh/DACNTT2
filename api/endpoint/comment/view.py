import uuid
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, Form
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
from api.base.authorization import get_current_user
from api.base.schema import SuccessResponse, FailResponse, ResponseStatus
from api.endpoint.comment.schema import ResponseComment, ResponseCreateUpdateComment
from api.library.constant import CODE_SUCCESS, TYPE_MESSAGE_RESPONSE, CODE_ERROR_COMMENT_CODE_NOT_FOUND, \
    CODE_ERROR_INPUT, CODE_ERROR_SERVER, CODE_ERROR_WHEN_UPDATE_CREATE_NOTI
from api.third_parties.cloud.query import upload_image_comment_cloud, delete_image, upload_image_cloud
from api.third_parties.database.query import comment as comment_query
from api.third_parties.database.query import post as post_query
from api.third_parties.database.query import user as user_query
from settings.init_project import open_api_standard_responses, http_exception
from api.third_parties.database.model.comment import Comment
from api.third_parties.database.query import notification as notification_query
from api.third_parties.database.model.notification import Notification

logger = logging.getLogger("comment.view.py")

router = APIRouter()


@router.get(
    path="/post/{post_code}/comments",
    name="get_all_comment",
    description="get all comment of post",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_200_OK,
        success_response_model=SuccessResponse[List[ResponseComment]],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def get_all_comment(post_code: str):
    try:
        if not post_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='post_code not allow empty')
        comments = await comment_query.get_all_comment_by_post_code(post_code)
        response = {
            "data": comments,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        print(response)
        return SuccessResponse[List[ResponseComment]](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.post(
    path="/post/{post_code}/comment",
    name="create_comment",
    description="create a comment",
    status_code=HTTP_200_OK,
    responses=open_api_standard_responses(
        success_status_code=HTTP_201_CREATED,
        success_response_model=SuccessResponse[ResponseCreateUpdateComment],
        fail_response_model=FailResponse[ResponseStatus]
    )
)
async def create_comment(
        post_code: str,
        content: str = Form(""),
        user: dict = Depends(get_current_user),
        image_upload: UploadFile = File(None)
):
    try:
        if not content and not image_upload:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='content, image upload not allow empty')

        image_id = ""
        image = ""

        if image_upload:
            data_image_byte = await image_upload.read()
            info_image_upload = await upload_image_cloud(data_image_byte, user['user_code'])
            image_id = info_image_upload['public_id']
            image = info_image_upload['url']

        comment_data = Comment(
            comment_code=str(uuid.uuid4()),
            content=content,
            created_by=user['user_code'],
            image_id=image_id,
            image=image,
            post_code=post_code
        )
        new_comment_id = await comment_query.create_comment(comment_data)
        new_comment = await comment_query.get_comment_by_id(new_comment_id)
        new_comment['created_by'] = user

        await post_query.push_comment_to_post(post_code, new_comment_id)  # push comment to post

        # Lấy thông tin bài viết
        post = await post_query.get_post_by_post_code(post_code)

        # Kiểm tra xem có phải chủ bài viết comment hay không
        # if user['user_code'] != post['created_by']:
        #     # Tạo notification
        #     notification = Notification(
        #         notification_code=str(uuid.uuid4()),
        #         user_code=post['created_by'],
        #         user_code_guest=user['user_code'],
        #         content=f"{user['fullname']} đã bình luận bài viết của bạn"
        #     )
        #     new_noti = await notification_query.create_noti(notification)
        #     if not new_noti:
        #         logger.error(TYPE_MESSAGE_RESPONSE[CODE_ERROR_WHEN_UPDATE_CREATE_NOTI])

            # # Gửi socket notification (nếu online)

        response = {
            "data": new_comment,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }
        print(response)
        return SuccessResponse[ResponseCreateUpdateComment](**response)

    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.delete(
    path="/post/{post_code}/comment/{comment_code}",
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
    try:
        if not comment_code:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='comment_code not allow empty')
        comment = await comment_query.get_comment_by_comment_code(comment_code)

        if not comment:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_COMMENT_CODE_NOT_FOUND)
        else:
            for image_id in comment.get("image_id", []):
                await delete_image(image_id)

        deleted = await comment_query.delete_comment(comment_code)
        if not deleted:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='Failed comment delete')

        return deleted
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )


@router.put(
    path="/post/{post_code}/comment/{comment_code}",
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
        user: dict = Depends(get_current_user),
        image_upload: UploadFile = File(None)

):
    try:
        if not comment_code and not content and not image_upload:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, message='comment_code, content, image upload '
                                                                            'not allow empty')
        image_id = []
        image = []

        comment_update = await comment_query.get_comment_by_comment_code(comment_code)
        if not comment_update:
            return http_exception(status_code=HTTP_400_BAD_REQUEST, code=CODE_ERROR_COMMENT_CODE_NOT_FOUND)

        list_image_need_delete_in_cloud = comment_update['image_id']

        if image_upload:
            data_image_byte = await image_upload.read()
            info_image_upload = await upload_image_comment_cloud(data_image_byte, user['user_code'])
            image_id.append(info_image_upload['public_id'])
            image.append(info_image_upload['url'])
            comment_update['image_id'] = image_id
            comment_update['image'] = image
            for image_ids in list_image_need_delete_in_cloud:
                print(image_ids)
                print(await delete_image(image_ids))

        if content:
            comment_update['content'] = content
        print(comment_update)

        new_comment = await comment_query.update_comment(comment_code, comment_update)
        print(new_comment)
        # user_of_comment = await user_query.get_user_by_code(new_comment[0]['user_code'])
        # for comment in new_comment:
        #     comment['created_by'] = user_of_comment
        new_comment['created_by'] = user

        response = {
            "data": new_comment,
            "response_status": {
                "code": CODE_SUCCESS,
                "message": TYPE_MESSAGE_RESPONSE["en"][CODE_SUCCESS],
            }
        }

        return SuccessResponse[ResponseCreateUpdateComment](**response)
    except:
        logger.error(exc_info=True)
        return http_exception(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_ERROR_SERVER,
        )
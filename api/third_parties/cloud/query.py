import cloudinary
import cloudinary.uploader
from settings.init_project import config_system

cloudinary.config(
    cloud_name=config_system['CLOUD_NAME'],
    api_key=config_system['CLOUD_API_KEY'],
    api_secret=config_system['API_SECRECT']
)


async def upload_image_cloud(file_data_stream, user_code):
    return cloudinary.uploader.upload(file_data_stream, folder=user_code)


async def upload_image_comment_cloud(file_data_stream, user_code, comment_code, img_id):
    return cloudinary.uploader.upload(file_data_stream, folder=f"{user_code}/{comment_code}/{img_id}")


async def upload_video(file_data_stream, user_code):
    return cloudinary.uploader.upload_large(file_data_stream,
                                            chunk_size=10000000)  # tối đa 10mb


async def delete_image(img_ids):
    return cloudinary.uploader.destroy(public_id=img_ids)


async def delete_video(video_id):
    return cloudinary.uploader.destroy(public_id=video_id)

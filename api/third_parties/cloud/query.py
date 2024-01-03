
import cloudinary
import cloudinary.uploader
from settings.init_project import config_system

print(config_system['CLOUD_NAME'], config_system['CLOUD_API_KEY'], config_system['API_SECRECT'])
cloudinary.config(
    cloud_name=config_system['CLOUD_NAME'],
    api_key=config_system['CLOUD_API_KEY'],
    api_secret=config_system['API_SECRECT']
)


async def upload_image_cloud(file_data_stream, user_code):
    cloudinary.uploader.upload(file_data_stream, folder=user_code)
from api.third_parties.database.model.notification import Notification
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_notification_id(notification_id):
    db = await MongoDBService().get_db()
    return await db['notification'].find_one({"_id": is_valid_object_id(notification_id)})


async def create_noti(noti: Notification):
    db = await MongoDBService().get_db()
    result = await db['notification'].insert_one(noti.to_json())
    return result.inserted_id

async def get_notification_by_code(notification_code):
    db = await MongoDBService().get_db()
    return await db['notification'].find_one({"_id": is_valid_object_id(notification_code)})


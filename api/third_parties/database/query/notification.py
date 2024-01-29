from api.third_parties.database.model.notification import Notification
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id
from api.third_parties.database.query.paging import paging


async def get_notification_id(notification_id):
    db = await MongoDBService().get_db()
    return await db['notification'].find_one({"_id": is_valid_object_id(notification_id)})


async def create_noti(noti: Notification):
    db = await MongoDBService().get_db()
    result = await db['notification'].insert_one(noti.to_json())
    return result.inserted_id


async def get_notifications(user_code, last_notification_id=""):
    db = await MongoDBService().get_db()

    list_notification_cursor = await paging(
        query_param_for_paging=last_notification_id,
        database_name="notification",
        query_condition={"user_code": user_code, "deleted_flag": False},
        db=db,
        sort=1)
    return list_notification_cursor


async def delete_notification(notification_code, user_code):
    db = await MongoDBService().get_db()
    result = await db['notification'].update_one(
        {"notification_code": notification_code, "user_code": user_code},
        {"$set": {"deleted_flag": True}}
    )
    return result.deleted_count


async def update_notification(notification_code, user_code):
    db = await MongoDBService().get_db()
    result = await db['notification'].update_one(
        {"notification_code": notification_code, "user_code": user_code},
        {"$set": {"is_checked": True}}
    )
    return result

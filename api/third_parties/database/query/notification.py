from api.third_parties.database.model.notification import Notification
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id
from api.third_parties.database.query.paging import paging_sort_by_create_time


async def get_notification_id(notification_id):
    db = await MongoDBService().get_db()
    return await db['notification'].find_one({"_id": is_valid_object_id(notification_id)})


async def get_notification_by_notification_code(notification_code: str):
    db = await MongoDBService().get_db()
    notification = await db['notification'].find_one({"notification_code": notification_code})
    return notification


async def create_noti(noti: Notification):
    db = await MongoDBService().get_db()
    result = await db['notification'].insert_one(noti.to_json())
    return result.inserted_id


async def get_all_notifications(user_code: str, last_notification_id=""):
    db = await MongoDBService().get_db()

    list_notification_cursor = await paging_sort_by_create_time(
        query_param_for_paging=last_notification_id,
        database_name="notification",
        query_condition={"user_code_guest": user_code, "deleted_flag": False},
        db=db,
        sort=1)
    return list_notification_cursor


async def delete_notification(notification_code, user_code: str):
    db = await MongoDBService().get_db()
    result = await db['notification'].find_one_and_update(
        {"notification_code": notification_code, "user_code_guest": user_code},
        {"$set": {"deleted_flag": True}}
    )
    return result


async def update_notification(notification_code, user_code: str):
    db = await MongoDBService().get_db()
    result = await db['notification'].find_one_and_update(
        {"notification_code": notification_code, "user_code_guest": user_code},
        {"$set": {"is_checked": True}}
    )
    return result

import uuid

from pymongo import ReturnDocument

from api.third_parties.database.model.post import Post
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_all_post_by_user_code(user_code):
    db = await MongoDBService().get_db()
    cursor = db['post'].find({"created_by": user_code})
    posts = await cursor.to_list(None)
    return posts


async def get_post_by_post_code(post_code: str):
    db = await MongoDBService().get_db()
    post = await db['post'].find_one({"post_code": post_code})
    return post


async def get_post_by_id(post_id):
    db = await MongoDBService().get_db()
    post = await db['post'].find_one({"_id": post_id})
    return post


async def create_post(data: Post):
    db = await MongoDBService().get_db()
    result = await db['post'].insert_one(data.to_json())
    return result.inserted_id


async def update_post(post_code, data_update):
    db = await MongoDBService().get_db()
    result = await db['post'].find_one_and_update(
        {"post_code": post_code},
        {"$set": data_update},
        return_document=ReturnDocument.AFTER
    )
    print(result)
    return result


async def delete_post(post_code):
    db = await MongoDBService().get_db()
    result = await db['post'].delete_one({"post_code": post_code})
    return result.deleted_count

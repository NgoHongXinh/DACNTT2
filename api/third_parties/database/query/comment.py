from api.third_parties.database.model.comment import Comment
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id
import uuid


async def get_comment_by_comment_code(comment_code: str):
    db = await MongoDBService().get_db()
    comment = await db['post'].find_one({"comment_code": comment_code})
    return comment


async def get_all_comment_by_post_code(post_code):
    db = await MongoDBService().get_db()
    comment = await db['comment'].find({"post_code": post_code})
    return comment


async def get_comment_by_id(comment_id):
    db = await MongoDBService().get_db()
    return await db['comment'].find_one({"_id": is_valid_object_id(comment_id)})


async def create_comment(data: Comment):
    db = await MongoDBService().get_db()
    print(data.comment_code)
    result = await db['comment'].insert_one(data.to_json())
    return result.inserted_id


async def delete_comment(comment_code):
    db = await MongoDBService().get_db()
    result = await db['comment'].delete_one({"comment_code": comment_code})
    return result.deleted_count


async def update_comment(comment_code, data_update):
    db = await MongoDBService().get_db()
    result = await db['comment'].update_one(
        {"comment_code": comment_code},
        {"$set": data_update.to_json()}
    )
    return result.upserted_id

import uuid

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


async def create_post(data):
    db = await MongoDBService().get_db()
    # post_code = str(uuid.uuid4())
    new_post = {
        'created_by': data.created_by,
        'content': data.content,
        'images': data.images,
        'image_ids': data.image_ids,
        'videos': data.videos,
        'video_ids': data.video_ids,
        'post_code': data.post_code
    }
    print(new_post)
    result = await db['post'].insert_one(new_post)
    return result.inserted_id


async def update_post(post_code, data_update):
    db = await MongoDBService().get_db()
    # update = {}
    # if content:
    #     update['content'] = content
    # if images:
    #     update['images'] = []
    # if video:
    #     update['video'] = ""
    #
    # print(update)
    # if update is not None:
    result = await db['post'].update_one(
        {"post_code": post_code},
        {"$set": data_update.to_json()}
    )
    return result.upserted_id


async def delete_post(post_code):
    db = await MongoDBService().get_db()
    result = await db['post'].delete_one({"post_code": post_code})
    return result.deleted_count

from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_all_post_by_user_code(user_code):
    db = await MongoDBService().get_db()
    cursor = db['post'].find({"created_by": user_code})
    posts = await cursor.to_list(None)
    return posts


async def get_post_by_user_code(user_code):
    db = await MongoDBService().get_db()
    post = await db['post'].find_one({"created_by": user_code})
    return post

async def create_post(user_code, content, images=[], video=None):
    db = await MongoDBService().get_db()
    new_post = {
        'created_by': user_code,
        'content': content,
        'images': images,
        'video': video
    }
    result = await db['post'].insert_one(new_post)
    return result.inserted_id

async def update_post(user_code, content, images=[], video=None):
    db = await MongoDBService().get_db()
    post = {
        'created_by': user_code,
        'content': content,
        'images': images,
        'video': video
    }
    result = await db['post'].update_one(post)
    return result.upserted_id

async def delete_post(post_code):
    db = await MongoDBService().get_db()
    result = await db['post'].delete_one({"_id": post_code})
    return result.deleted_count
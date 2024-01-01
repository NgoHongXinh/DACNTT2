from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_post_by_user_code(user_code):
    db = await MongoDBService().get_db()
    cursor = db['post'].find({"created_by": user_code})
    posts = await cursor.to_list(None)
    return posts

async def get_post_by_code(post_code):
    db = await MongoDBService().get_db()
    return await db['post'].find_one({"_id": is_valid_object_id(post_code)})


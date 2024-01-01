from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_comment_id(comment_id):
    db = await MongoDBService().get_db()
    return await db['comment'].find_one({"_id": is_valid_object_id(comment_id)})

async def get_comment_by_code(comment_code):
    db = await MongoDBService().get_db()
    return await db['comment'].find_one({"_id": is_valid_object_id(comment_code)})


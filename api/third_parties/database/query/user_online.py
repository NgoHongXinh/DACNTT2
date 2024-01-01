from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_user_online_id(user_online_id):
    db = await MongoDBService().get_db()
    return await db['user_online'].find_one({"_id": is_valid_object_id(user_online_id)})

async def get_user_online_by_code(user_online_code):
    db = await MongoDBService().get_db()
    return await db['user_online'].find_one({"_id": is_valid_object_id(user_online_code)})


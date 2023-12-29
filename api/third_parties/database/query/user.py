from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_user_id(user_id):
    db = await MongoDBService().get_db()
    return await db['account'].find_one({"_id": is_valid_object_id(user_id)})

async def get_user_by_code(user_code):
    db = await MongoDBService().get_db()
    return await db['account'].find_one({"_id": is_valid_object_id(user_id)})


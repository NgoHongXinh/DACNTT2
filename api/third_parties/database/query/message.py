from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_message_id(message_id):
    db = await MongoDBService().get_db()
    return await db['message'].find_one({"_id": is_valid_object_id(message_id)})

async def get_message_by_code(message_code):
    db = await MongoDBService().get_db()
    return await db['message'].find_one({"_id": is_valid_object_id(message_code)})


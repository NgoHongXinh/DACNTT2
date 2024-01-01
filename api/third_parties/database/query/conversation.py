from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_conversation_id(conversation_id):
    db = await MongoDBService().get_db()
    return await db['conversation'].find_one({"_id": is_valid_object_id(conversation_id)})

async def get_conversation_by_code(conversation_code):
    db = await MongoDBService().get_db()
    return await db['conversation'].find_one({"_id": is_valid_object_id(conversation_code)})


from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_friend_request_id(friend_request_id):
    db = await MongoDBService().get_db()
    return await db['friend_request'].find_one({"_id": is_valid_object_id(friend_request_id)})

async def get_friend_request_by_code(friend_request_code):
    db = await MongoDBService().get_db()
    return await db['friend_request'].find_one({"_id": is_valid_object_id(friend_request_code)})


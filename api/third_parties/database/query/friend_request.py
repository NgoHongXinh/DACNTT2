from api.third_parties.database.model.friend_request import FriendRequest
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_friend(user_code_request, user_code_receive_request):
    db = await MongoDBService().get_db()
    return await db['friend_request'].find_one({
        "user_code_request": user_code_request,
        "user_code_receive": user_code_receive_request
    })


async def create_fr(friend_request: FriendRequest):
    db = await MongoDBService().get_db()
    result = await db['friend_request'].insert_one(friend_request.to_json())
    return result.inserted_id


async def get_friend_request_by_code(friend_request_code):
    db = await MongoDBService().get_db()
    return await db['friend_request'].find_one({"_id": is_valid_object_id(friend_request_code)})


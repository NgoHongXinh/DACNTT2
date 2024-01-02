from api.library.function import verify_password, get_password_hash
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id


async def get_user_id(user_id):
    db = await MongoDBService().get_db()
    return await db['user'].find_one({"_id": is_valid_object_id(user_id)})


async def check_user(username: str, password: str):
    db = await MongoDBService().get_db()
    user = await db['user'].find_one({"username": username})
    if user:
        check_pass = await verify_password(password, user['password'])
        if check_pass:
            return user
    return None


async def get_user_by_code(user_code):
    db = await MongoDBService().get_db()
    return await db['user'].find_one({"user_code": user_code})




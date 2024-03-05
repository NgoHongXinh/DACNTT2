from api.third_parties.database.model.conversation import Conversation
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id
from api.third_parties.database.query.paging import paging_sort_by_create_time, paging


async def get_conversation_by_code(conversation_code):
    db = await MongoDBService().get_db()
    return await db['conversation'].find_one({"conversation_code": conversation_code})


async def get_all_conversation_of_current_user(user_code: str, last_conversation_id=""):
    db = await MongoDBService().get_db()
    list_conversation_cursor = await paging(
        query_param_for_paging=last_conversation_id,
        database_name="conversation",
        query_condition={"members": {"$in": [user_code]}},
        db=db,
        sort=1)
    return list_conversation_cursor


async def create_conversation(data: Conversation):
    db = await MongoDBService().get_db()
    result = await db['conversation'].insert_one(data.to_json())
    return result.inserted_id


async def get_conversation_by_members(members):
    db = await MongoDBService().get_db()
    return await db['conversation'].find_one({"members": {"$all": members}})


async def get_max_stt(user_code):
    db = await MongoDBService().get_db()
    return db['conversation'].find({"members": {"$in": [user_code]}}).sort("stt", -1).limit(1)
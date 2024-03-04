from api.third_parties.database.model.group import Group
from api.third_parties.database.mongodb import MongoDBService, is_valid_object_id
from api.third_parties.database.query.paging import paging_sort_by_create_time, paging


async def get_group_by_code(group_code):
    db = await MongoDBService().get_db()
    return await db['group'].find_one({"group_code": group_code})


async def get_group_by_id(group_id):
    db = await MongoDBService().get_db()
    return await db['group'].find_one({"_id": is_valid_object_id(group_id)})


async def get_all_group_of_current_user(user_code: str, last_group_id=""):
    db = await MongoDBService().get_db()
    list_group_cursor = await paging(
        query_param_for_paging=last_group_id,
        database_name="group",
        query_condition={"members": {"$in": [user_code]}},
        db=db,
        sort=1)
    return list_group_cursor


async def create_group(data: Group):
    db = await MongoDBService().get_db()
    result = await db['group'].insert_one(data.to_json())
    return result.inserted_id


async def get_group_by_members(members):
    db = await MongoDBService().get_db()
    return await db['group'].find_one({"members": {"$all": members}})


async def add_user_to_group(user_code, group_code):
    db = await MongoDBService().get_db()
    group = await db['group'].find_one({"group_code": group_code})

    if user_code not in group['members']:
        group['members'].append(user_code)

    result = await db['group'].find_one_and_update(
        {"group_code": group_code},
        {"$set": group}
    )
    return result
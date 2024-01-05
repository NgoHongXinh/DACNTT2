from typing import Union

from motor.motor_asyncio import AsyncIOMotorDatabase

from api.third_parties.database.mongodb import is_valid_object_id


def paging_aggregation(
        query_param_for_paging: str,
        database_name: str,
        key_query: str,
        value_query: Union[str, dict],
        db: AsyncIOMotorDatabase,
        foreign_table: str = "None",
        local_field: str = "None",
        foreign_field: str = "None",
        show_value: dict = None,  # sau khi query sẽ hiển thị những field nào, mặc định hiển thị hết
        sort: int = 1  # sort : -1 descending, 1 ascending
):
    object_id = is_valid_object_id(query_param_for_paging)

    query_greater_than_or_less_than = "$gt"  # query lớn hơn
    if sort == -1:
        query_greater_than_or_less_than = "$lt"  # query bé hơn

    cursor = db[database_name].aggregate(
        [
            {
                "$match": {
                    "$and": [{key_query: value_query}, {"_id": {query_greater_than_or_less_than: object_id}}]
                }
            } if query_param_for_paging else {
                "$match": {key_query: value_query}
            },
            {
                "$lookup": {
                    "from": foreign_table,
                    'localField': local_field,
                    'foreignField': foreign_field,
                    "as": f'{foreign_table}_document'
                }
            },
            {"$project": show_value} if show_value else {'$unset': f"{show_value}"},
            {"$sort": {"_id": sort}},
            {"$limit": 20}
        ]
    )

    return cursor

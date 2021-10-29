
from re import A
from typing import Dict, List


from utils import functions as _func
from utils import type as _type
from utils import path as _path
from utils import parse as _parse
from utils import format as _format

from discord.ext.commands import Context

USER_DESCRIPTION_PROPERTY_NAME = 'Name'
USER_KEY_NAME = 'Id'



async def get_users_infos_by_name( aUserName: str ) -> List[_type.EntityInfo]:
    user_infos = list( (await __get_users_data( aUserName ) ).values())
    return user_infos


async def __get_users_data( aUserName: str) -> _type.EntitiesData:
    sPath = await  _path.__get_users_data_path( aUserName )
    raw_data = await _func.get_data_from_path( sPath )
    user_infos = _parse.__xmltree_to_dict( raw_data, 3 )
    return user_infos



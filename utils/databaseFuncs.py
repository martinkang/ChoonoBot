from typing import Any, Callable, Dict, List, Tuple, Union

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import database as db
from . import settings as _set
from . import functions as _func
from . import time as _time

# column name, type, primary key, not null
ColumnDefinition = Tuple[str, str, bool, bool]
ColumnData = Tuple[str, any]


def _create_schema() -> bool:
    global gColumn_Definitions_PSS_ACCESS_KEY
    
    gColumn_Definitions_PSS_ACCESS_KEY = [
        ('Access_Key', 'TEXT(50)', False, True),
        ('Login_Date', 'TEXT(50)', False, True)
    ]
    

async def _initSchema():
    await _initAccessKey()
    
async def _initAccessKey():
    await db.try_Create_Table( "PSS_ACCESS_KEY_TABLE", gColumn_Definitions_PSS_ACCESS_KEY )
    sSuccess, sResultList = await db.select_Table( "PSS_ACCESS_KEY_TABLE" )
    
    if len(sResultList) == 0:
        await db.insertAccessKeyData( "AccessKey", _time.PSS_START_DATETIME )
    else:
        for sKey, sLastLogin in sResultList:
            _func.gAccessKey['Key'] = sKey
            _func.gAccessKey['LastLogin'] = _time.datetime.strptime( sLastLogin, _time.DATABASE_DATETIME_FORMAT )
    
    _func.debug_log( "_initAccessKey", f'Success : {sSuccess}' )

 
    
def _getColumnInDefination( aColName: str, aColType: str, aColIsPrimary: bool = False, aColIsNotNull: bool = False ) -> str:
    sCols = []
    sColNameTxt = aColName.lower()
    sColTypeTxt = aColType.upper()

    if aColIsPrimary:
        sCols.append('PRIMARY KEY')
    if aColIsNotNull:
        sCols.append('NOT NULL')

    sResult = f'{sColNameTxt} {sColTypeTxt}'
    if sCols:
        sResult += ' ' + ' '.join(sCols)
    return sResult.strip()

    
def _getColumnListInDefination( aColumnDefinitions: List[ColumnDefinition] ) ->str:
    sColList = []
    for sColName, sColType, sColIsPrimary, sColIsNotNull in aColumnDefinitions:
        sColList.append( _getColumnInDefination( sColName, sColType, sColIsPrimary, sColIsNotNull ) )
    
    return ', '.join(sColList)

import calendar

from utils import functions as _func
from utils import time as _time
from utils import database as _db
from utils import type as _type
from utils import path as _path
from utils import parse as _parse
from utils import emojis as _emojis
from typing import List

from discord.utils import escape_markdown

import pss_lookups as lookups


ALLOWED_DIVISION_LETTERS: List[str] = sorted([letter for letter in lookups.DIVISION_CHAR_TO_DESIGN_ID.keys() if letter != '-'])
DIVISION_DESIGN_DESCRIPTION_PROPERTY_NAME: str = 'DivisionName'
DIVISION_DESIGN_KEY_NAME: str = 'DivisionDesignId'

EXCEL_FLEET_NUM: int = 7



def isDivisionLetter( aStr: str ) -> bool:
    sResult = False
    if aStr is None:
        sResult = False
    else:
        sResult = aStr.lower() in [letter.lower() for letter in ALLOWED_DIVISION_LETTERS]
    return sResult


async def getOnlineDivisionStarsData():
    sPath = await _path.__get_search_all_fleets_stars()
    sRawData = await _func.get_data_from_path( sPath )

    sFleet_infos = _parse.__xmltree_to_dict( sRawData, 3 )
    sDvisions = {}
    for division_design_id in lookups.DIVISION_DESIGN_ID_TO_CHAR.keys():
        if division_design_id != '0':
            sDvisions[division_design_id] = [fleet_info for fleet_info in sFleet_infos.values() if fleet_info[_path.DIVISION_DESIGN_KEY_NAME] == division_design_id]


    return sDvisions


def getOnlineTotalDivisionStars( aDivisionStars ):
    result = None

    if aDivisionStars:
        divisions_texts = []
        for division_design_id, fleet_infos in aDivisionStars.items():
            divisions_texts.append((division_design_id, __get_division_stars_as_text(fleet_infos)))

        sNow = _time.get_utc_now()
        sDivision = { '1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        for division_design_id, division_text in divisions_texts:
            sTitle = f'{sNow.month}월 토너먼트 {sDivision[division_design_id]}' 
            result.append(sTitle)
            result.extend(division_text)
            result.append(_type.ZERO_WIDTH_SPACE) 

    return result


def getOnlineDivisionStars( aDivisions, aDivisionStars ):
    result = None

    if aDivisionStars:
        divisions_texts = []
        sDivision = { '1': 'A', '2': 'B', '3': 'C', '4': 'D'}

        for division_design_id, fleet_infos in aDivisionStars.items():
            if sDivision[division_design_id] == aDivisions.upper():
                divisions_texts.append((division_design_id, __get_division_stars_as_text(fleet_infos)))

        sNow = _time.get_utc_now()  
        for division_design_id, division_text in divisions_texts:
            sTitle = f'{sNow.month}월 토너먼트 {sDivision[division_design_id]}' 
            result.append(sTitle)
            result.extend(division_text)
            result.append(_type.ZERO_WIDTH_SPACE) 
            break

    return result

def getOnlineFleetIDs( aDivisionStars ):
    sResult = []
    
    for division_design_id, fleet_infos in aDivisionStars.items():
        for i, fleet_info in enumerate(fleet_infos, start=1):
            sTuple = ()
            fleet_id = escape_markdown(fleet_info['AllianceId'])
            sScore = escape_markdown(fleet_info['Score'])
            sTuple = (int(division_design_id), fleet_id, int(sScore) )
            sResult.append(sTuple)
        
    sResult.sort(key=lambda x:(x[0], -x[2] ))
  
    return sResult



async def getStarsEachFleet( aWB, aDiv, aNo, aKey, aFleetID, aNow, aTest ):
    sPath = await _path.__get_search_fleet_users_base_path( aKey, aFleetID )
    sRawData = None
    
    while sRawData is None:
        sRawData = await _func.get_data_from_path( sPath )
        if sRawData is None:
            print( "Sleep For GetData")
            _time.sleep(10)
        else:
            break;

    sFleet_infos = _parse.__xmltree_to_dict( sRawData, 3 )
    sAlianceName = None
    sResult = ''
    sDesc = ''
    for user_info in sFleet_infos.values():
        if sAlianceName is None:
            sAlianceName = user_info['AllianceName']
            if aTest == True:
                sDesc =  f'No / Get Stars (Stars Score) / Name / Trophy'
            else:
                sDesc =  f'No / Get Stars / Name / Trophy'
            break;

    sStarsList = []
    sTuple = ()
    for user_info in sFleet_infos.values():
        if sAlianceName is None:
            sAlianceName = user_info['AllianceName']
            
        sStar, sStarData = _db.getTourneyScores( user_info, aTest )
        sTuple = ( int(sStar), sStarData )
        sStarsList.append(sTuple)

    sNum = 0
    sStarsTxt = ''
    sStarsList.sort(key=lambda x:x[0], reverse=True)
    for sStars in sStarsList:
        sNum = sNum + 1
        sStarsTxt = sStarsTxt + f'{sNum} / ' + str( sStars[1] ) + '\n'
        
        if sNum == 30:
            break

    sResult = sDesc + '\n' + sStarsTxt + '\n'
    
    return sAlianceName, sResult



def __get_division_stars_as_text(fleet_infos: List[_type.EntityInfo]) -> List[str]:
    lines = []
    fleet_infos = _func.sort_entities_by(fleet_infos, [('Score', int, True)])
    fleet_infos_count = len(fleet_infos)
    for i, fleet_info in enumerate(fleet_infos, start=1):
        fleet_name = escape_markdown(fleet_info['AllianceName'])
        additional_info: List[_type.Tuple[str, str]] = []
        trophies = fleet_info.get('Trophy')
        if trophies:
            additional_info.append((trophies, _emojis.trophy))
        member_count = fleet_info.get('NumberOfMembers')
        if member_count:
            additional_info.append((str(member_count), _emojis.members))
        stars = fleet_info['Score']
        if i < fleet_infos_count:
            difference = int(stars) - int(fleet_infos[i]['Score'])
        else:
            difference = 0
        if additional_info:
            additional_str = f' ({" ".join([" ".join(info) for info in additional_info])})'
        else:
            additional_str = ''
        lines.append(f'**{i:d}.** {stars} (+{difference}) {_emojis.star} {fleet_name}{additional_str}')
    return lines




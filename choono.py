import sys
from asyncio.tasks import sleep
from typing import Dict, List

# --------------- Utils ---------------
from utils import functions as _func
from utils import database as db
from utils import format as _format

# --------------- Schedule --------------- 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time

# --------------- User Module ---------------
import pss_user as _user
import pss_ship as _ship


# --------------- Discord -------------------
import discord, os
import asyncio
from discord.ext import commands
from discord.ext.commands import context
from utils import time as _time



import pss_tournament 


#==============================================================================================
# Constant
#==============================================================================================
NEED_SHIP_INFO: bool = True
DO_NOT_NEED_SHIP_INFO: bool = False

#==============================================================================================
# Global Variables
#==============================================================================================
gBot = commands.Bot(command_prefix='-', status=discord.Status.online, activity=discord.Game("-냥냥냥") )


#==============================================================================================
# Temporary User List
#==============================================================================================
sRussian = []
sRussian.append( { 'Id' : '5195724', 'Name' : 'SPACE ENEMY' } )
sRussian.append( { 'Id' : '3433365', 'Name' : 'atomic samurai' } ) 
sRussian.append( { 'Id' : '2135741', 'Name' : 'tezzar' } )
sRussian.append( { 'Id' : '6606727', 'Name' : 'xBiGx' } )
sRussian.append( { 'Id' : '3608200', 'Name' : 'volax' } )
sRussian.append( { 'Id' : '2819541', 'Name' : 'Cpt. Laser Beard' } ) 
sRussian.append( { 'Id' : '4703085', 'Name' : 'Zlоdey' } )
sRussian.append( { 'Id' : '1228935', 'Name' : 'Taska' } )
sRussian.append( { 'Id' : '6420614', 'Name' : 'AlfaR1' } )
sRussian.append( { 'Id' : '3145262', 'Name' : 'Giallar' } )
    
#==============================================================================================
# Bot Schedule Event Sub Functions
#==============================================================================================
async def getListUserInfosByFunction( aUserList, aTitle:str, aIsNeedShipInfo:bool, aFormatFunc ):
    sOutputEmbed = None

    sOutputList = ''
    sNow = _time.get_utc_now()
    
    for sUser in aUserList:
        sInfosTxt = None
        sIsLogin = False
        sUserInfos = await _user.get_users_infos_by_name( sUser['Name'] )  
        try:
            for sUserInfo in sUserInfos:
                print( f'User ID {sUser["Id"]}  sUserInfo ID : {sUserInfo["Id"]}' )
                if sUser['Id'] == sUserInfo['Id']:
                    sShipInfo = None
                    if aIsNeedShipInfo is True:
                        sShipInfo = await _ship.get_Inspect_Ship_info( sUserInfo['Id'] )
                        _, sInfosTxt = aFormatFunc( sNow, sUserInfo, sShipInfo, True )
                    else:
                        _, sInfosTxt = aFormatFunc( sNow, sUserInfo, None, True )
                        
                    break    
        except Exception as sEx:
            print( f'getTopUserInfosByFunction Exception {sEx}' )
        
        if sInfosTxt is not None:
            sOutputList = sOutputList + f'{sInfosTxt}' + '\n'
        else:
            if sIsLogin == True:
                print( f'{sUser["Name"]} 는 로그인 중입니다')
            else:
                print( f'{sUser["Name"]} 를 찾지 못했습니다')

    sOutputEmbed = discord.Embed(title=aTitle, description=sOutputList, color=0x00aaaa)
        
    return sOutputEmbed


#==============================================================================================
# Bot Schedule Event
#==============================================================================================
@gBot.event
async def getLastDayStars():
    print("getLastDayStars")
    sChannel = gBot.get_channel(int(os.environ.get( 'CHOONO_CANNEL_ID' )))

    sOutputEmbed = None
    sNow = _time.get_utc_now()
    if _time.isTourneyStart():
        sDivisionStars = await pss_tournament.getOnlineDivisionStarsData()
        sFleetDatas = pss_tournament.getOnlineFleetIDs( sDivisionStars )

        sKey = await _func.get_access_key()
        for sFleetData in sFleetDatas:
            if sFleetData[0] == 1:
                sFleetName, sOutputEmbed = await pss_tournament.getStarsEachFleet( sKey, sFleetData[1], sNow )
                sEmb = discord.Embed(title=f'{sFleetName} Stars Score', description=sOutputEmbed, color=0x00aaaa)   
                await sChannel.send(embed=sEmb)
            else:
                break

        return
        
   
@gBot.event
async def chaseListUsers():
    print("chaseListUsers")
    sChannel = gBot.get_channel(int(os.environ.get( 'CHOONO_CANNEL_ID' )))
   
    try:
        sOutputEmbed = await getListUserInfosByFunction( sRussian,
                                                        f'랭킹. 유저(함대) / 트로피 / 접속 / 보호막',
                                                        NEED_SHIP_INFO, 
                                                        _format.create_User_Immunity )  
        sOutputEmbed.set_footer(text="약 10분 정도 오차가 존재할 수 있습니다.")
    except Exception as sERR:
        sErrTxt = f'에러발생 : {sERR}'
        sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
        
    await sChannel.send(embed=sOutputEmbed)
  
#==============================================================================================
# Initialize Bot
#==============================================================================================
@gBot.event
async def on_ready():
    print( 'Logged in as' )
    print( 'User Name : ' + gBot.user.name )
    print( 'Bot ID    : ' + str(gBot.user.id) )
    print( '--------------' )
    
    sched = AsyncIOScheduler(timezone='UTC')
    sched.start()
    sched.add_job( getLastDayStars, 'cron', hour='23', minute='55', id="touney_save" )
    sched.add_job( chaseListUsers, 'interval', minutes=3 )
    print( 'Tourney Schedule Start' )
    


async def initBot(): 
    print( 'init Bot' )
    try:
        _time.init()
        print( 'Time Function initilaize Success' )
        _func.init()
        print( 'Internal Function initilaize Success' )
        await db._init()
        print( 'Database initilaize Success' )            

        print( 'init Bot Success' )
    except Exception as sEx:
        print( 'init Bot Failure : ' + str(sEx) )
        sys.exit()

    sKey = await _func.get_access_key()
    print( "initBot AccessKey : ", sKey )
   
if sys.platform == 'win32':
    # Set the policy to prevent "Event loop is closed" error on Windows - https://github.com/encode/httpx/issues/914
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
if __name__ == "__main__":  
    asyncio.run( initBot() )
     
#asyncio.create_task(pingDatatbase())
gBot.run( os.environ.get('CHOONO_BOT_TOKEN') )


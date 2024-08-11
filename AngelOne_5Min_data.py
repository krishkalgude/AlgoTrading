from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import websocket
import pandas as pd
import login as l

#-------------------------------------LOGIN PROCESS--------------------------------------------


api_key = 'nC****i7'
username = 'R****70'
pwd = '****'
smartApi = SmartConnect(api_key)
try:
    token = "75JKO2ZF32KHDGRVDA*******M"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)

if data['status'] == False:
    logger.error(data)
    
else:
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
  
    feedToken = smartApi.getfeedToken()
 
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    res=res['data']['exchanges']
obj=SmartConnect(api_key=l.api_key)
data=obj.generateSession(l.user_name,l.password,totp)
refreshToken=data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()
l.feed_token=feedToken
#fetch User profile
userProfile=obj.getProfile(refreshToken)
print(userProfile)
# Historic API
def OHLCHistory(symbol,token,interval,fdate,todate):
    try:
        historicParam={
            "exchange":"NSE",
            "tradingsymbol":symbol,
            "symboltoken":token,
            "interval":interval,
            "fromdate":fdate,
            "todate":todate
        }
        history=obj.getCandleData(historicParam)['data']
        history=pd.DataFrame(history)
        history=history.rename(
            columns={0:"Datetime",1:"open",2:"high",3:"low",4:"close",5:"Volume"})
        history['Datetime']=pd.to_datetime(history['Datetime'])
        history=history.set_index('Datetime')
        return history
    except Exception as e:
        print("Historic API Failed:{}".format(e))
print("Daily data:")
Dailydata=OHLCHistory("SBI-EQ","3045","ONE_DAY","2023-02-01 00:00","2024-02-01 15:30")
my_df=pd.DataFrame(Dailydata)
print(my_df)
my_df.to_csv(r'{}.csv'.format('NIFTY_oneday'),mode='a',index=True,header=False)
minute5data=OHLCHistory("SBI-EQ","3045","FIVE_MINUTE","2024-01-02 9:15","2024-01-02 15:30")
print("5 minute data:")
my_df=pd.DataFrame(Dailydata)
print(my_df)
my_df.to_csv(r'{}.csv'.format('NIFTY_5minute'),mode='a',index=True,header=False)
print("End Program")
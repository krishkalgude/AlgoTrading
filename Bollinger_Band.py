from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import websocket
import pandas as pd
import login as l
import xlwings as xw
import matplotlib.pyplot as plt

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
def Bollinger_Band(DF,n,std):
    df=DF.copy()
    df["MA"]=df['close'].rolling(n).mean()
    df["BB_up"]=df["MA"]+std*df['close'].rolling(n).std(ddof=0)
    df["BB_dn"]=df["MA"]-std*df['close'].rolling(n).std(ddof=0)
    df["BB_width"]=df["BB_up"]-df["BB_dn"]
    df.dropna(inplace=True)
    return df
one_day_dataframe=OHLCHistory("SBI-EQ","3045","ONE_DAY","2024-06-01 00:00","2024-07-24 15:30")
Band=Bollinger_Band(one_day_dataframe,20,2)
#print(Band)
wb=xw.Book('store.xlsx')
B_band=wb.sheets("BOLLINGER_BAND")
B_band.range("A1").value=Band

# Function to plot Bollinger Bands and save as PNG
def plot_B_band(df, save_file):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['close'], label='Close Price')
    plt.plot(df.index, df['MA'], label='Moving Average', linestyle='--')
    plt.plot(df.index, df['BB_up'], label='Upper Bollinger Band', linestyle='--', color='tab:blue')
    plt.plot(df.index, df['BB_dn'], label='Lower Bollinger Band', linestyle='--', color='tab:blue')
    plt.fill_between(df.index, df['BB_up'], df['BB_dn'], alpha=0.1, color='tab:blue')
    plt.title('Bollinger Bands')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Save the plot as PNG
    plt.savefig(save_file)
    plt.close()

# Assuming Band is the DataFrame returned from Bollinger_Band function
plot_B_band(Band, 'bollinger_bands.png')

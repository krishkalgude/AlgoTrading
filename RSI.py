from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import websocket
import pandas as pd
import login as l
import xlwings as xw
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.dates as mdates

#-------------------------------------LOGIN PROCESS--------------------------------------------


api_key = 'nC****i7'
username = 'R****70'
pwd = '****'
smartApi = SmartConnect(api_key)
try:
    token = "75JKO2ZF32KHDGRVD*******QM"
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

def RSI(df,n):
    delta=df["close"].diff().dropna()
    u=delta*0
    d=u.copy()
    u[delta>0]=delta[delta>0]
    d[delta<0]=-delta[delta<0]
    u[u.index[n-1]]=np.mean(u[:n])
    u=u.drop(u.index[:(n-1)])
    d[d.index[n-1]]=np.mean(d[:n])
    d=d.drop(d.index[:(n-1)])
    rs=u.ewm(com=n,min_periods=n).mean()/d.ewm(com=n,min_periods=n).mean()
    return 100-100/(1+rs)
one_day_dataframe=OHLCHistory("SBI-EQ","3045","ONE_DAY","2024-04-01 00:00","2024-07-29 15:30")
rsi=RSI(one_day_dataframe,14)
#print(rsi)
wb=xw.Book('store.xlsx')
R_S_I=wb.sheets("RSI")
R_S_I.range("A1").value=rsi
def plot_rsi(df):
    """Plot RSI values and save as a PNG file."""
    plt.figure(figsize=(12, 6))
    
    # Plot RSI values
    plt.plot(df.index, df, label='RSI', color='blue')
    
    # Add horizontal lines for RSI levels
    plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    
    # Format the x-axis to show dates clearly
    #plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    #plt.gcf().autofmt_xdate()
    
    plt.title('Relative Strength Index (RSI)')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PNG file
    plt.savefig('RSI_plot.png', format='png')
    
    # Optionally, show the plot
    # plt.show()


plot_rsi(rsi)
from SmartApi import SmartConnect
import pyotp
from logzero import logger
import pandas as pd
import xlwings as xw
import matplotlib.pyplot as plt
import login as l

#-------------------------------------LOGIN PROCESS--------------------------------------------

api_key = 'nC****i7'
username = 'R****70'
pwd = '****'
smartApi = SmartConnect(api_key)
try:
    token = "75JKO2ZF32KHDGRVD*******M"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

data = smartApi.generateSession(username, pwd, totp)
if data['status'] == False:
    logger.error(data)
else:
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    feedToken = smartApi.getfeedToken()
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    res = res['data']['exchanges']

obj = SmartConnect(api_key='nCHOeUi7')  # Update accordingly
data = obj.generateSession(username, pwd, totp)
refreshToken = data['data']['refreshToken']
feedToken = obj.getfeedToken()
l.feed_token = feedToken
userProfile = obj.getProfile(refreshToken)
print(userProfile)

# Historic API
def OHLCHistory(symbol, token, interval, fdate, todate):
    try:
        historicParam = {
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "interval": interval,
            "fromdate": fdate,
            "todate": todate
        }
        history = obj.getCandleData(historicParam)['data']
        history = pd.DataFrame(history)
        history = history.rename(
            columns={0: "Datetime", 1: "open", 2: "high", 3: "low", 4: "close", 5: "Volume"})
        history['Datetime'] = pd.to_datetime(history['Datetime'])
        history = history.set_index('Datetime')
        return history
    except Exception as e:
        print("Historic API Failed:{}".format(e))

def MACD(DF, len1, len2, len3):
    df = DF.copy()
    df["MA_Fast"] = df["close"].ewm(span=len1, min_periods=len1).mean()
    df["MA_Slow"] = df["close"].ewm(span=len2, min_periods=len2).mean()
    df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
    df["Signal"] = df["MACD"].ewm(span=len3, min_periods=len3).mean()
    df.dropna(inplace=True)
    return df

one_day_dataframe = OHLCHistory("SBI-EQ", "3045", "ONE_DAY", "2024-03-01 00:00", "2024-07-29 15:30")
macd = MACD(one_day_dataframe, 12, 26, 9)

def plot_macd(df):
    plt.figure(figsize=(12, 6))
    #plt.plot(df.index, df['close'], label='Close Price', color='blue')
    plt.plot(df.index, df['MACD'], label='MACD', color='green')
    plt.plot(df.index, df['Signal'], label='Signal Line', color='red')
    plt.title('MACD Plot')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.savefig('macd_plot.png')  # Save the plot to a file
    plt.close()  # Close the plot to free memory

plot_macd(macd)

# Save to Excel
wb = xw.Book('store.xlsx')
Macd = wb.sheets("MACD")
Macd.range("A1").value = macd

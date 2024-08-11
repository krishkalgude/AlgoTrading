from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import websocket
import pandas as pd
import login as l
import xlwings as xw
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
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

def shooting_star(ohlc_df):
    df=ohlc_df.copy()
    df["s_star"]=(((df["high"]-df["low"])>3*(df["open"]-df["close"])) & \
                  ((df["high"]-df["close"])/(0.001+df["high"]-df["low"])>0.6)& \
                  ((df["high"]-df["open"])/(0.001+df["high"]-df["low"])>0.6))& \
                  (abs(df["close"]-df["open"])>0.1*(df["high"]-df["low"]))
    return df
one_day_dataframe=OHLCHistory("SBI-EQ","3045","ONE_DAY","2024-06-20 00:00","2024-07-24 15:30")
shooting_s=shooting_star(one_day_dataframe)
#print(shooting_s)
#wb=xw.Book('store.xlsx')

#S_STAR=wb.sheets("SHOOTING_STAR")
#S_STAR.range("A1").value=shooting_s


def plot_shooting_star(df):
    """Plot candlestick data and highlight shooting star patterns."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Convert dates to numeric values for plotting
    dates = mdates.date2num(df.index)
    
    # Plot each candlestick
    for i in range(len(df)):
        color = 'green' if df.iloc[i]['close'] >= df.iloc[i]['open'] else 'red'
        ax.plot([dates[i], dates[i]], [df.iloc[i]['low'], df.iloc[i]['high']], color='black', lw=1)  # High-low line
        ax.add_patch(patches.Rectangle(
            (dates[i] - 0.2, df.iloc[i]['open']),
            width=0.4,  # Width of the candlestick
            height=df.iloc[i]['close'] - df.iloc[i]['open'],
            color=color
        ))

    # Highlight shooting stars
    shooting_stars = df[df['s_star']]
    ax.scatter(mdates.date2num(shooting_stars.index), shooting_stars['high'], color='blue', marker='o', label='Shooting Star')

    # Formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()

    ax.set_title('Shooting Star Patterns in Candlestick Chart')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)

    # Save the plot as a PNG file
    plt.savefig('shooting_star_plot.png', format='png')

    # Optionally, show the plot
    # plt.show()

# Example usage
one_day_dataframe = OHLCHistory("SBI-EQ", "3045", "ONE_DAY", "2024-06-20 00:00", "2024-07-24 15:30")
shooting_s = shooting_star(one_day_dataframe)
wb = xw.Book('store.xlsx')
S_STAR = wb.sheets("SHOOTING_STAR")
S_STAR.range("A1").value = shooting_s

# Plot and save shooting star plot
plot_shooting_star(shooting_s)

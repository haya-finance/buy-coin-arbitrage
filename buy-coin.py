##pkg
import okx.Trade as Trade
from binance.spot import Spot
import pandas as pd

##info
#money
MONEY=    #int

#ok:str


apikey_ok = 
secretkey_ok = 
passphrase = 

#bian: str
api_key_bian=
api_secret_bian=

##connect
#ok
flag = "1"  # 实盘: 0, 模拟盘: 1

tradeAPI = Trade.TradeAPI(apikey_ok, secretkey_ok, passphrase, False, flag)

#bian
client = Spot(api_key=api_key_bian, api_secret=api_secret_bian)

##
#amount_calculate
data=pd.read_csv('')     #data_all_market.csv  # update per sason
symbol=list(set(list(data['symbol'])))
##remove stablecoin,memes coin
symbol.remove('USDT')
symbol.remove('USDC')
symbol.remove('DAI')
symbol.remove('DOGE')
symbol.remove('SHIB')
symbol.remove('PEPE')
symbol.remove('WIF')
symbol.remove('FLOKI')
##select
data=data.sort_values(by='market_cap_usd',ascending=False)[0:30]
data['weight']=[i/data['market_cap_usd'].sum() for i in data['market_cap_usd']]
df1=data

a=len([i for i in df1['weight'] if i>0.3])
if a>0:
    df1['weight']=[0.3]+[i*0.7/df1[1:]['market_cap_usd'].sum() for i in df1[1:]['market_cap_usd']]
a=len([i for i in df1['weight'] if i>0.3])
if a>0:
    df1['weight']=[0.3,0.3]+[i*0.4/df1[2:]['market_cap_usd'].sum() for i in df1[2:]['market_cap_usd']]
a=len([i for i in df1['weight'] if i>0.3])
if a>0:
    df1['weight']=[0.3,0.3,0.3]+[i*0.1/df1[3:]['market_cap_usd'].sum() for i in df1[3:]['market_cap_usd']]
for  i in len(df1):
    if df1['market'][i]=='bian':
        params = {
        'symbol': df1['symbol'][i],
        'side': '   BUY',
        'type': 'MARKET',
        'timeInForce': 'GTC',
        'quantity': MONEY*df1['weight'][i]/df1['price']
        }
        response = client.new_order(**params)
        print(response)
    
    if df1['market'][i]=='ok':
        result = tradeAPI.place_order(
            instId=df1['symbol'][i],
            tdMode="cash",
            side="buy",
            ordType="market",
            sz=str(MONEY*df1['weight'][i]/df1['price'])
        )

        print(result)

#market to wallet address

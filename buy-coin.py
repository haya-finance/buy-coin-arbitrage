##pkg
import okx.Trade as Trade
import okx.Funding as Funding
from binance.spot import Spot
import pandas as pd
import time

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

#top up address:  str
to_address_binance=
to_address_binance=


##connect
#ok
flag = "0" 

tradeAPI = Trade.TradeAPI(apikey_ok, secretkey_ok, passphrase, False, flag)

#bian
client = Spot(api_key=api_key_bian, api_secret=api_secret_bian)


## get_balance of exchanges

def bian_balance():
    response = client.user_asset(recvWindow=10000)
    print(response)
    symbol_bian=[]
    dic_bian_balance={}
    for i in range(len(response)):
        symbol_bian.append(response[i]['asset'])
        dic_bian_balance[response[i]['asset']]=response[i]['free']
    print(symbol_bian)
    print(dic_bian_balance)
    return dic_bian_balance

def ok_balance():
    result = fundingAPI.get_balances()
    symbol_ok=[]
    dic_ok_balance={}
    for i in range(len(result['data'])):
        symbol_ok.append(result['data'][i]['ccy'])
        dic_ok_balance[result['data'][i]['ccy']]=result['data'][i]['bal']

    print(symbol_ok)
    print(dic_ok_balance)
    return dic_ok_balance



##wallet_to_exchange_to_wallet

'''
money:           int; unit:wei  depend on the decimal of the token
to_address1:     str; top up address of the exchange
token_on_wallet: str; token needed to change 
'''
def to_exchange(money,to_address1,token_on_wallet):      
    amount=money
    CONTRACT_ADDRESS=token_on_wallet
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    to_address=to_address1
    gas=contract.functions.transfer(to_address,
        amount).estimate_gas({'from':wallet_address})
    print(gas)
    print(w3.eth.gas_price)

    transaction = contract.functions.transfer(to_address,
        amount).build_transaction({
            'chainId':w3.eth.chain_id,
            'from': caller,
            'nonce': nonce
        })

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=account_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

'''
binance to wallet

!! this method will tranfer all the assert in the symbols list of binance needed to buy

!! this method should wait for second minutes

symbol:     str;  like 'ETH','BTC','USDT'
'''
def bian_out(symbol):
    dic=bian_balance()

    client.withdraw(coin=symbol, amount=float(dic[symbol]), address=wallet_address,network='ARBITRUM',recvWindow=10000)

'''
ok to wallet

!! should add wallet_address to the white list first

symbol:     str;  like 'ETH','BTC','USDT'

'''

def ok_out(symbol):
    dic=ok_balance()
    result = fundingAPI.withdrawal(
        ccy=symbol,
        toAddr=wallet_address,
        amt=str(dic[symbol]),
        fee="0.0001",
        dest="4", 
        chain="ETH-Arbitrum One"
    )


##trade_on_exchange

'''
binance trade

pair:  str;  like 'ETHUSDT'
money: int;  usdt value of the symbol

'''


def bian_trade(pair,money):
    params = {
        'symbol': pair,
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': money,   #U
        'recvWindow':10000,
    }

    response = client.new_order(**params)
    print(response)

'''
okex trade

pair:   str;   like'ETH-USDT' 
money:  str;   amount of symbol

'''

def ok_trade(pair,SIDE,money):
    flag = "0"
    tradeAPI = Trade.TradeAPI(apikey_ok, secretkey_ok, passphrase, False, flag)
    result = tradeAPI.place_order(
        instId=pair,
        tdMode="cash",   
        side=SIDE,
        ordType="market",
        sz=money     
    )


##ok transfer 
'''
assert account <> trade account 


from/to:   str; '18':fund-account '6'：trade-account

'''
def ok_transfer(symbol,money,from_1,to_1):
    flag = "0"  # 实盘: 0, 模拟盘: 1
    fundingAPI=Funding.FundingAPI(apikey_ok, secretkey_ok, passphrase, False, flag)
    result = fundingAPI.funds_transfer(
        ccy=symbol,
        amt=money,
        from_=from_1,   #资金账户
        to=to_1      #交易账户
    )
    print(result)




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



binance_amount=sum(list(df1[df1['exchange']=='binance']['weight'].values))
okex_amount=sum(list(df1[df1['exchange']=='okex']['weight'].values))

binance_amount_usdt=MONEY*binance_amount
okex_amount_usdt=MONEY*okex_amount

to_exchange(binance_amount_usdt*100000,to_address_binance,usdt)
to_exchange(okex_amount_usdt*1000000,to_address_okex,usdt)
for i in range(0,10000):
    time.sleep(60)
    dic_binance=bian_balance()
    dic_ok=ok_balance()
    if dic_binance['USDT']>binance_amount_usdt*0.99 and dic_ok['USDT']>ok_amount_usdt*0.99:
        break
    else:
        continue

if ok_amount_usdt>0:
    ok_transfer('USDT',dic_ok['USDT'],'18','6')

for  i in range(len(df1)):
    if df1['market'][i]=='bian':
        bian_trade(df1['symbol'][i]+'USDT',MONEY*df1['weight'][i])

    if df1['market'][i]=='ok':
        ok_trade(df1['symbol'][i]+'-'+'USDT','BUY',MONEY*df1['weight'][i])
        dic_ok=ok_balance()
        ok_transfer(df1['symbol'][i],dic_ok[df1['symbol'][i]],'6','18')

for i in range(len(df1)):
    if df1['market'][i]=='bian':
        bian_out(df1['symbol'][i])

    if df1['market'][i]=='ok':
        ok_out(df1['symbol'][i])


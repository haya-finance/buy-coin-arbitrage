import buy_coin_config as config
from web3 import Web3
import json
import time
import okx.Trade as Trade
import okx.Funding as Funding
import okx.MarketData as okmarket
import okx.Account as okaccount
import pandas as pd
from binance.spot import Spot
import time
import math

max_approval_hex = f"0x{64 * 'f'}"
max_approval_int = int(max_approval_hex, 16)

###web3
account_provider=config.arb_wallet_provider
wallet_address=config.metamask_address
account_private_key=config.arb_wallet_private_key


w3 = Web3(Web3.HTTPProvider(account_provider))
w3.eth.defaultAccount = wallet_address
caller = wallet_address
nonce = w3.eth.get_transaction_count(caller)



##前置工作
bian_client=Spot(api_key=config.api_key_bian, api_secret=config.api_secret_bian)
okmarketapi = okmarket.MarketAPI(config.api_ok, config.apikey_ok, config.ok_pass, False, '0',debug =False)  #实盘0
symbol1=pd.read_excel('symbol.xlsx')

symbol=list(symbol1['symbol'].values)
dic_exchange={}
for i in range(len(symbol)):
    dic_exchange[symbol1['symbol'][i]]=symbol1['exchange'][i]

dic_weight={}
for i in range(len(symbol)):
    dic_weight[symbol1['symbol'][i]]=float(symbol1['weight'][i])

dic_prices={}
def price_update():
    for i in symbol:
        if dic_exchange[i]=='bian':
            dic_prices[i]=float(bian_client.klines(i+'USDT', "1m",limit=1)[0][4])
        elif dic_exchange[i]=='okx':
            dic_prices[i]=float(okmarketapi.get_candlesticks(i+'-USDT',limit='2')['data'][0][4])


price_update()
price=sum([dic_weight[i]*float(dic_prices[i]) for i in symbol])


h20='0x250f93c92AEbF7304c9e7e347D1acA8C0212Edea'
weth='0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
pool=w3.to_checksum_address('0x396EEdd12A43E68ecAca80021Db4F2E398dC88A0')
with open('pool_abi.json', 'r') as file:
    pool_abi = json.load(file)
pool= w3.eth.contract(address=pool, abi=pool_abi)
# print(pool.functions.token0().call())
# print(pool.functions.token1().call())




# reserve = pool.functions.getReserves().call({'from': wallet_address})
# print(reserve[0]/10**18)
# print(reserve[1]/10**18)




arb_swap_address='0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24'
with open('arbabi.json', 'r') as file:
    arb_swap_abi = json.load(file)

arb_contract=w3.eth.contract(address=arb_swap_address, abi=arb_swap_abi)

def swap(amount,path):
    transaction = arb_contract.functions.swapExactTokensForTokens(int(amount*10**18),0, path,caller,round(time.time())+60*20).build_transaction({
                "from": caller,
                "chainId":w3.eth.chain_id,
                "nonce": w3.eth.get_transaction_count(caller),
            })

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

with open('uniswaperc20.json', 'r') as file:
    erc20_abi = json.load(file)

def approved_amount(token, contract):
    erc20_contract = w3.eth.contract(
        address=w3.to_checksum_address(token), abi=erc20_abi)
    approved_amount = erc20_contract.functions.allowance(wallet_address, contract).call()
    return approved_amount

#print(approved_amount(weth, arb_swap_address))

def approve1(address,abi,contract1,nonce):
    contract = w3.eth.contract(address=address, abi=abi)
    transaction = contract.functions.approve(contract1,max_approval_int).build_transaction({
            'chainId':w3.eth.chain_id,
            'from': caller,
            'nonce': nonce
        })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=account_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

waiting_list=[weth,h20]
num1=0
for i in waitinglist:
    if approved_amount(i, arb_swap_address)==0:
        approve1(i,erc20_abi,arb_swap_address,nonce+num1)
        num1+=1


def cal_amount(amountA,amountB,inputA):      ##计算滑点之后得到的数量
    L=amountA*amountB
    outputB=amountB-L/(amountA+inputA)
    return outputB

while True:
    time.sleep(300)   #秒
    price_update()
    index_price=sum([dic_weight[i]*float(dic_prices[i]) for i in symbol])/dic_prices['ETH']
    

    reserve = pool.functions.getReserves().call({'from': caller})
    h20_amount=reserve[0]/10**18
    weth_amount=reserve[1]/10**18
    L=h20_amount*weth_amount
    print(h20_amount)
    print(weth_amount)
    current_price2=weth_amount/h20_amount
    if index_price>current_price2:       ##二级价格低 用钱包weth 换 h20出来  池子h20 变少


        weth_adjust=math.sqrt(weth_amount*h20_amount*index_price)-weth_amount
        
        h20_adjust=h20_amount-h20_amount*weth_amount/(weth_amount+weth_adjust)
 
        h20_price_cost=weth_adjust/h20_adjust
        print(h20_price_cost)
        
        if weth_adjust*dic_prices['ETH']<1000:
            if (index_price-h20_price_cost)/index_price>0.03:
                swap(weth_adjust,[weth,h20])
                print(1)


        elif weth_adjust*dic_prices['ETH']>1000:
            if (index_price-h20_price_cost)/index_price>0.003:
                swap(weth_adjust,[weth,h20])
                print(2)
        

    if index_price<current_price2:        ##二级价格高 用钱包h20 换 weth 出来  池子h20 变多


        h20_adjust=math.sqrt(weth_amount*h20_amount/index_price)-h20_amount

        weth_adjust=weth_amount-h20_amount*weth_amount/(h20_amount+h20_adjust)
        
        h20_price_cost=weth_adjust/h20_adjust
        print(h20_price_cost)

        if h20_price_cost>index_price:
             
            if weth_adjust*dic_prices['ETH']<1000:
                if (h20_price_cost-index_price)/index_price>0.03:
                    swap(h20_adjust,[h20,weth])
                    print(3)


            elif weth_adjust*dic_prices['ETH']>1000:
                if (h20_price_cost-index_price)/index_price>0.003:
                    swap(h20_adjust,[h20,weth])
                    print(4)
from uniswap import Uniswap
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3 import middleware


import json

##  apply for a api_key of conmarketcap
API_KEY =   #str
headers = {
    'X-CMC_PRO_API_KEY': API_KEY
}
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=600'

##pool contract  && set contract     str
pool_contracr=  
set_contract=     

##quantity_usdt

quantity_usdt=    ##int
range=        ##float

##token weight

data=      ##pd.read_csv

data_weight={}
symbol=list(data['symbol'].values)

for i in range(len(data)):
    data_weight[data['symbol'][i]]=data['wight'][i] 

##abi
with open('aa3.json', 'r') as file:
    data = json.load(file)

with open('aa4.json', 'r') as file:
    data1 = json.load(file)

with open('aa6.json', 'r') as file:
    data2 = json.load(file)

##basic_address
issue_basic_address=     #"0xdf4D6165797Af392eBD4D1F552145c2906e61E0b"
trade_basic_address=     # "0x882D62FFAAD9eAE169E8Acb219B26b0f071A70B0"
set_contract=            #'0x22F489d624F87017f7C8429e20De5E551a333BDa'


##connect
#info
account_provider=    
wallet_address=
account_private_key=



#uniswap-connect
w3 = Web3(Web3.HTTPProvider(account_provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
address = wallet_address
private_key = account_private_key
version = 3
uniswap = Uniswap(address=address, private_key=private_key, version=version, web3=w3)

#get_balance
token1=     #'0x8c7da66e7a3a75a844b4faa04058b17bcfffab5c'
balance=uniswap.get_token_balance(token1)
print(balance)

#web3-connect
w3 = Web3(Web3.HTTPProvider(account_provider))
w3.eth.defaultAccount = wallet_address
caller = wallet_address
nonce = w3.eth.get_transaction_count(caller)

def issue(amount):
    issue_contract = w3.eth.contract(address=issue_basic_address, abi=initialAbi)
    transaction = issue_contract.functions.issue(set_contract,
        amount, wallet_address).build_transaction({
            'chainId':w3.eth.chain_id,
            'from': caller,
            'nonce': nonce
        })

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

def redeem(amount):
    issue_contract = w3.eth.contract(address=issue_basic_address, abi=initialAbi)
    transaction = issue_contract.functions.redeem(set_contract,
        amount, wallet_address).build_transaction({
            'chainId':w3.eth.chain_id,
            'from': caller,
            'nonce': nonce
        })

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

#循环
a=1
while a>0:
    r = requests.get(url, headers=headers)
    find_prices = {}
    if r.status_code == 200:
        data = r.json()
        for d in data['data']:
            symbol = d['symbol']
            find_prices[symbol] =d['quote']['USD']['price']   

    price_set=sum([find_prices.get(i)*data_weight.get(i) for i in symbol])
    price_swap=uniswap.get_price_output(token_set,token_usdt,quantity_usdt,fee)

    if (price_swap-price_set)/price_set> range:

        issue(quantity_usdt)

        uniswap.make_trade(set_contract,usdt_contract,quantity_usdt)


    
    if (price_set-price_swap)/price_ser> range:

        uniswap.make_trade(usdt_contract,set_contract,quantity_usdt)

        redeem(quantity_usdt)


















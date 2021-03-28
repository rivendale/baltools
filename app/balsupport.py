from flask import flash, redirect, render_template, url_for
from datetime import datetime
import os, sys, json, array, math, requests
from time import time, sleep
from operator import itemgetter
from operator import attrgetter
from decimal import *
from app.models import *


# Needed to calc today and yesterday timestamps
from time import time

# COINGECKO API
# https://www.coingecko.com/en/api
# https://www.coingecko.com/en/api#explore-api
# https://assets.coingecko.com/reports/API/CoinGecko-API-Deck.pdf
# https://coingecko.com/api/documentations/v3


def checkspamtoken(tokenaddress):
    spamlist = ["0x04ad70466a79dd1251f22ad426248088724ff32b","0x0deecb13f4e801bdbf2721875756d44b207ca580","0x1234567461d3f8db7496581774bd869c83d51c93",
    "0x15e4cf1950ffa338ce5bc59456b3e579ed1bead3","0x1e28439d814486c9d989e55b1993c2f1447957cc","0x253f6e0bfe6c7675e8513b4c132f00b00b951d5e",
    "0x2630997aab62fa1030a8b975e1aa2dc573b18a13","0xedf44412b47a76e452fd133794e45d9485e4cd4b","0x888666ca69e0f178ded6d75b5726cee99a87d698",
    "0x322f4f6a48329690957a3bcbd1301516c2b83c1f","0x3a4a0d5b8dfacd651ee28ed4ffebf91500345489","0x3a7ebc138fd59ccce16b7968199c2ac7b013bbc0",
    "0x3da85b2a7cf6f3ccec6953776161750681a7560f","0x4022eb64d742d88f71070ba6a1fcbb5d11275a9f","0x426ca1ea2406c07d75db9585f22781c096e3d0e0",
    "0x429ac77f069bff489e2d78f9479e1e933305c528","0x47f32f9ebfc49a1434eb6190d5d8a80a2dc36af5","0x4c1c4957d22d8f373aed54d0853b090666f6f9de",
    "0x4c6112f9652463f5bdcb954ff6b650acb64e47cc","0x4dc3643dbc642b72c158e7f3d2ff232df61cb6ce","0x5245789633b5d0ebd21e393c3d7ead22d5ad1517",
    "0x52903256dd18d85c2dc4a6c999907c9793ea61e3","0x5b46b3705dbe773ffa878aa4ff064522ce347275","0x639ae8f3eed18690bf451229d14953a5a5627b72",
    "0x63a18bc38d1101db7f0efcbcbdcbe927a5879039","0x68e14bb5a45b9681327e16e528084b9d962c1a39","0x708b63545467a9bcfb67af92299102c650e34a0e",
    "0x72adadb447784dd7ab1f472467750fc485e4cb2d","0x741d63278490a33f705519cfd5c56fe470726ee8","0x75efc1111f98f2d5dcec9851c8abc77cd5e6ced8",
    "0x77fe30b2cf39245267c0a5084b66a560f1cf9e1f","0x7995ab36bb307afa6a683c24a25d90dc1ea83566","0x7b2f9706cd8473b4f5b7758b0171a9933fc6c4d6",
    "0x7b53b2c4b2f495d843a4e92e5c5511034d32bd15","0x7d3e7d41da367b4fdce7cbe06502b13294deb758","0x7f1f2d3dfa99678675ece1c243d3f7bc3746db5d",
    "0x80d607b3ede3b3ebd55fcf1369882d0b668b9be2","0x8c4e7f814d40f8929f9112c5d09016f923d34472","0x8e4fbe2673e154fe9399166e03e18f87a5754420",
    "0x8f7b0b40e27e357540f90f187d90ce06366ac5a5","0x977b0584b50cdd64e2f8185b682a1f256448c7c8","0x9c5c3395b9b791d2edd472592045fb341e115c3b",
    "0x9fe173573b3f3cf4aebce5fd5bef957b9a6686e8","0xa2dca1505b07e39f96ce41e875b447f46d50c6fc","0xa38b7ee9df79955b90cc4e2de90421f6baa83a3d",
    "0xaa1bbd948a0a4835e45f672d34f50eed819a9255","0xac9bb427953ac7fddc562adca86cf42d988047fd","0xae66d00496aaa25418f829140bb259163c06986e",
    "0xaf47ebbd460f21c2b3262726572ca8812d7143b0","0xb7fbe91752dd926a5ea103f1b2e8b6fd2cee4d91","0xbab6f30c81209433a3ced28ca8e19256440547d9",
    "0xbddab785b306bcd9fb056da189615cc8ece1d823","0xbf4a2ddaa16148a9d0fa2093ffac450adb7cd4aa","0xc12d1c73ee7dc3615ba4e37e4abfdbddfa38907e",
    "0xc3761eb917cd790b30dad99f6cc5b4ff93c4f9ea","0xc92e74b131d7b1d46e60e07f3fae5d8877dd03f0","0xcdc7faa3a06733d50d4bf86b5c7cd9460c35691e",
    "0xd037a81b22e7f814bc6f87d50e5bd67d8c329fa2","0xd51e852630debc24e9e1041a03d80a0107f8ef0c","0xdb455c71c1bc2de4e80ca451184041ef32054001",
    "0xdff3718cd0fda48e045bac6ad66950fa259f51b5","0xe03b4386b75e121e04d580d6b8376ceee0615ca8","0xedf44412b47a76e452fd133794e45d9485e4cd4b",
    "0xf18432ef894ef4b2a5726f933718f5a8cf9ff831","0xf3e014fe81267870624132ef3a646b8e83853a96","0xf6276830c265a779a2225b9d2fcbab790cbeb92b",
    "0xf6317dd9b04097a9e7b016cd23dcaa7cfe19d9c6","0x58b6a8a3302369daec383334672404ee733ab239"]

    if tokenaddress in spamlist:
        return True
    else:
        return False

def getBalancer(ethaddress):
    # https://github.com/balancer-labs/balancer-subgraph
    # Subgraph: https://thegraph.com/explorer/subgraph/balancer-labs/balancer

    balancerurl = 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer'
    now = int(time())
    today = now-math.floor(now%86400) # get timestamp at start of day
    yesterday = today-86400

    ####### OBTAIN TOTAL NUMBER OF POOLS
    datanumpools = '''
    query
    {
        balancers {
        poolCount
        }
    }
    '''
    responsenumpools = requests.post(balancerurl,json={'query': datanumpools})
    numpooldata = responsenumpools.content
    testdata = json.loads(numpooldata)['data']['balancers']
    testdata = str(testdata[0]["poolCount"])
    ##################################
######## OBTAIN ALL POOL SHARE INFO: User Address, Token Symbol & Name, Balance
    totallcv = 0
    ethstring = '"' + ethaddress + '"'

    while True:
        lcv = 0
        dataquery = '''
                query
                {
                    poolShares (first: 1000, skip: '''+str(totallcv)+''', where: {userAddress:'''+ethstring+'''})
                    {
                        userAddress
                          {
                          id
                          sharesOwned {
                            balance
                          }
                          }
                          balance
                        poolId (first: 1000, where: {active: true })
                           {
                           id
                           totalShares
                           totalSwapVolume
                           swapFee
                           tokens
                              {
                              symbol
                              name
                              balance
                              address
                              }
                            swaps (first: 1,orderBy: timestamp,orderDirection: desc,where:{timestamp_lt: '''+str(yesterday)+'''})
                               {
                                tokenIn
					            tokenInSym
					            tokenAmountIn
					            tokenOut
					            tokenOutSym
					            tokenAmountOut
					            poolTotalSwapVolume
                               }
                            }
                      }
                }
        '''

        response = requests.post(balancerurl,json={'query': dataquery})
        data = response.content  
           
        infodata = []
        LPassets = []
        totalrev = 0
        currpool = "NONE"

        for pool in json.loads(data)['data']['poolShares']:
            lcv += 1
            totallcv += 1
            numtokens = 0
            useraddress = str(pool["userAddress"]["id"])
            userbpt = Decimal(pool["balance"])
            thispool = pool["poolId"]
            poolid = thispool["id"]
            totalshares = Decimal(thispool["totalShares"])
            poolvol = Decimal(thispool["totalSwapVolume"])
            swapfee = Decimal(thispool["swapFee"])
            tokens = thispool["tokens"]
            swapinfo = thispool["swaps"]
            if (swapinfo):
                swapvol = swapinfo[0]["poolTotalSwapVolume"]
                swapvol = Decimal(poolvol) - Decimal(swapvol)
                if (swapvol < 1):
                    swapvol = Decimal(0)
                else:
                    swapvol = round(swapvol,0)
            else:
                swapvol = 0

            swapfee = Decimal(swapfee)
            swapvol = Decimal(swapvol)
            if (totalshares < 1):
                balance = 0.0
                poolpct = 0.0
            else:
                poolpct = Decimal(1 - ((totalshares-userbpt) / totalshares))

                rev = Decimal(swapfee) * Decimal(swapvol) * Decimal(poolpct)
                totalrev = totalrev + rev
                tokenswap = Decimal(swapfee*100)

                for token in tokens:
                    numtokens = numtokens + 1

                if (numtokens > 0):
                    tokenrev = round((rev / numtokens),2)
                    tokenrev = round(Decimal(tokenrev),4)
                    tokenpct = Decimal(poolpct * 100)
                    tokenpct = round(tokenpct,2)
                else:
                    tokenrev = 0
                    tokenpct = 0

                for token in tokens:
                    symbol = str(token["symbol"]).upper()
                    name = str(token["name"])
                    balance = Decimal(token["balance"])
                    tokenaddress = str(token["address"])
                    balance = balance * poolpct
                    balance =Decimal(balance)


                    if (balance > 0.0):
                        if (int(float(balance)) > 4):
                            balance = math.trunc(balance)
                        else:
                            balance=Decimal(str(balance)).quantize(Decimal('.001'), rounding=ROUND_DOWN)
                        balance = float(balance)
                        tokenrev=str(tokenrev)
                        swapvol=str(swapvol)
                        tokenswap=str(tokenswap)
                        tokenpct=str(tokenpct)
                        totalshares=str(totalshares)
                        userbpt=str(userbpt)
                        # Reducing Coingecko calls due to rate limits
                        price = 0.0
                        value = 0.0
                        sortval = 0.0
                        price = str(price)
                        value = str(value)
                        balance = str(balance)
                        infodata.append(BalancerInfo(price=price,value=value,rev=tokenrev,swapvol=swapvol,swapfee=tokenswap,tokenaddress=tokenaddress,poolpct=tokenpct,totalshares=totalshares,userbalance=userbpt,useradr=useraddress,symbol=symbol,name=name,qty=balance,poolid=poolid))
                        LPassets.append(EthTokens(price=price,value=value,symbol=symbol,name=str(name),tokenaddress=tokenaddress,qty=balance,sortval=sortval))
                            
                            
        if (lcv < 1000):
            break

    totalrev = str(round(Decimal(totalrev),2))

    return infodata,totalrev, LPassets

def consolidate(wallets,pools):
    # Use Coingecko for pricing via tokenaddress
    #url2 = "https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses=" + tokenaddress +"&vs_currencies=usd"
    errors = False
    totalvalue = 0.0 
    # Combine all tokens and quantities from wallet tokens and Balancer pools together
    alltokens = wallets + pools
    totals = []
    tokensets = []
    subcount = 0
    keepcount = 0
    junktokens = 0

    # go thru each token one at a time, looking for duplicate entries between Balancer pools and Wallet tokens
    for alltoken in alltokens:
        tokenaddress = alltoken.tokenaddress
        # this creates a single token list, ensuring no duplicate entries
        if tokenaddress not in tokensets:
            tokensets.append(tokenaddress)   # this will be a clean list of all tokens - only one entry per token type

    for tokenset in tokensets:  # now that we have a single list to loop thru, we're now searching thru the entire list (with duplicates possibly)
        qty = 0.0 # zero out the totals each iteration (unique so no repeats now) - as we know tokenset is a single list, we can iterate thru adding - use a float
        for alltoken in alltokens: # tokenset is the clean list that gets iterated thru, each entry searches thru the token list, add duplicates together for totals
            if tokenset == alltoken.tokenaddress:  # as tokenset is a subsection of alltokens, there will be at least a single entry, there may be duplicates across pools and wallet
                qty += float(alltoken.qty)   # # in case of duplicates all totals together
                symbol = alltoken.symbol  
                name = alltoken.name
                price = 0.0
                tokenaddress = alltoken.tokenaddress
                value = 0.0
                sortval = 0.0
        if checkspamtoken(tokenaddress):
            junktokens += 1
        else:
            if tokenaddress == "0xa0446d8804611944f1b527ecd37d7dcbe442caba":  # staked 1INCH
                tokenaddress = "0x111111111117dc0aa78b770fa6a738034120c302"
            cgurl = "https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses=" + tokenaddress +"&vs_currencies=usd"
            try:
                cgresp = requests.get(cgurl)
                cgdata = cgresp.json()
                price = Decimal(cgdata[tokenaddress]["usd"])
            except:
                #msg = "Error Saving token: Symbol: " + str(symbol) + " Name: " + str(name) + " Balance " + str(qty) + " Price: " + str(price) + " Total Value: " + str(value) + " address: " + str(tokenaddress) + " sortval: " + str(sortval)
                #flash(msg)
                errors = True
                msg1 = sys.exc_info()[0]
                msg2 = str(cgresp)
            if price < 100.0:
                price = float(price)
                price=round(price,4)
            else:
                price = math.trunc(price)
                price = float(price)
            sortval = float(price * qty)
            value = round(sortval,4)
            qty = str(qty)
            subcount += 1
            if subcount > 98:
                subcount = 0
                #flash ("maximum API calls to Coingecko reached, need to pause for 60 seconds")
                sleep(60)
            if sortval > 5.0:
                totalvalue += sortval
                totals.append(EthTokens(price=str(price),value=str(value),sortval=sortval,symbol=str(symbol),name=name,tokenaddress=tokenaddress,qty=qty))   

   # if errors:
       # flash(msg1)
       # flash(msg2)   
   
    totals = sorted(totals,key=attrgetter('sortval'),reverse=True)
    return totals,totalvalue


def getEthWalletTokens(ethaddy):
    # https://ethereum.stackexchange.com/questions/34335/etherscan-api-get-all-token-balances
    # https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API
    # https://ethplorer.io/wallet/#api
    # ETHPLORERKEY = "freekey"
    ETHPLORERKEY = app.config["ETHPLORERAPI"]
    url = "http://api.ethplorer.io/getAddressInfo/" + str(ethaddy) + "?apiKey=" + ETHPLORERKEY
    # token info: getTokenInfo
    tokenlist = []
    foundBPT = False
    totalvalue = 0.0

    response = requests.get(url)
    if response.status_code == 200:
        # Etherscan - Address info
        content = response.json()

        # Obtain Ethereum wallet balance 
        ethbalance = Decimal(content['ETH']['balance'])
        ethbalance = round(ethbalance,4)
        # Obtain wallet ERC-20 token balances
        totalcount = len(content['tokens'])   # total ERC-20 tokens
        lcv = 0 # set counter to 0 for first ERC-20 token 
        while True: # loop until counter completes final token in wallet
            token = content['tokens'][lcv]       
            tokeninfo = token['tokenInfo']
            notLP = True
            if tokeninfo['holdersCount'] > 0:
                try:   
                    balance = Decimal(token['balance'])
                    decimals = tokeninfo['decimals']
                    decimals = 10 ** int(decimals)
                    balance = Decimal(balance / decimals)
                    symbol = str(tokeninfo['symbol']).upper()
                    symlen = len(symbol)
                    tokenaddress = str(tokeninfo['address'])
                    tokenaddylen = len(tokenaddress)
                    name = str(tokeninfo['name'])
                    if symbol == "BPT":
                        foundBPT = True
                        notLP = False

                    rules = [balance > 0.0,
                             symlen > 1,
                             symlen < 8,
                             tokenaddylen > 1,
                             notLP]
                    if all(rules):
                        if balance < 100.0:
                            balance = float(balance)
                            balance=round(balance,4)    
                        else:
                            balance = math.trunc(balance)
                            balance = round(balance)
                        if balance > 0.0:   # removed Coingecko to address rate limiting
                            qty = str(balance)
                            price = 0.0
                            sortval = 0.0
                            value = 0.0
                            value = str(value)
                            price = str(price)

                            tokenlist.append(EthTokens(price=price,value=value,symbol=symbol,name=name,tokenaddress=tokenaddress,qty=qty,sortval=sortval))
  
                
                except:
                    errormsg = "Error reading token " + str(symbol)
                   # flash(errormsg)
  
            lcv = lcv + 1 
            if (lcv == totalcount):
                break
    tokenlist = sorted(tokenlist,key=attrgetter('tokenaddress')) 
    totalvalue = str(totalvalue)
    return tokenlist,foundBPT,ethbalance,totalvalue
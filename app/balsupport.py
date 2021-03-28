from flask import flash, redirect, render_template, url_for
from datetime import datetime
import os, sys, json, array, math, time, requests
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
    spamlist = ["0x426ca1ea2406c07d75db9585f22781c096e3d0e0"]
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
        if subcount > 7:
            subcount = 0
            keepcount = 0
            while keepcount < 500000000:
                keepcount += 1
        if sortval > 5.0:
            totalvalue += sortval
            totals.append(EthTokens(price=str(price),value=str(value),sortval=sortval,symbol=str(symbol),name=name,tokenaddress=tokenaddress,qty=qty))   

    if errors:
        flash(msg1)
        flash(msg2)        
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
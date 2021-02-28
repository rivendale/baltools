from flask import flash, redirect, render_template, url_for
from datetime import datetime
import os, sys, json, array, math, time, csv, io, requests, math
from operator import itemgetter
from operator import attrgetter
from decimal import *
from app.models import *

# Needed to calc today and yesterday timestamps
from time import time

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

                        balance=str(balance)
                        tokenrev=str(tokenrev)
                        swapvol=str(swapvol)
                        tokenswap=str(tokenswap)
                        tokenpct=str(tokenpct)
                        totalshares=str(totalshares)
                        userbpt=str(userbpt)

                        infodata.append(BalancerInfo(rev=tokenrev,swapvol=swapvol,swapfee=tokenswap,tokenaddress=tokenaddress,poolpct=tokenpct,totalshares=totalshares,userbalance=userbpt,useradr=useraddress,symbol=symbol,name=name,qty=balance,poolid=poolid))

        if (lcv < 1000):
            break

    totalrev = str(round(Decimal(totalrev),2))



    return infodata,totalrev


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


    response = requests.get(url)
    if response.status_code == 200:
        content = response.json()

        # Obtain Ethereum wallet balance 
        ethbalance = Decimal(content['ETH']['balance'])
        ethbalance = round(ethbalance,4)
        tokenlist.append(EthTokens(symbol="ETH",name="Ethereum",qty=str(ethbalance),tokenaddress="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"))

        

        # Obtain wallet ERC-20 token balances
        totalcount = len(content['tokens'])   # total ERC-20 tokens
        lcv = 0 # set counter to 0 for first ERC-20 token 
        while True: # loop until counter completes final token in wallet
            token = content['tokens'][lcv]       
            tokeninfo = token['tokenInfo']
            if tokeninfo['holdersCount'] > 0:
                try:   
                    notLP = True
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
                        
                        try:
                            if balance > 0.0: 
                                qty = str(balance)
                                tokenlist.append(EthTokens(symbol=symbol,name=name,qty=qty,tokenaddress=tokenaddress))
                                #msg = "OK reading token " + str(symbol) + " " + str(name) + " " + str(balance) + " " + str(tokenaddress)
                                #flash(msg)
                        except:
                            msg = "Error Calculating token " + str(symbol) + " " + str(name) + " " + str(balance) + " " + str(tokenaddress)
                            #flash(msg)
                except:
                    errormsg = "Error reading token " + str(symbol)
                    flash(errormsg)
  
            lcv = lcv + 1 
            if (lcv == totalcount):
                break
     
    return tokenlist,foundBPT
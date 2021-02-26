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

                        infodata.append(BalancerInfo(rev=tokenrev,swapvol=swapvol,swapfee=tokenswap,tokenaddress=tokenaddress,poolpct=tokenpct,totalshares=totalshares,userbalance=userbpt,useradr=useraddress,sym=symbol,name=name,qty=balance,poolid=poolid))

        if (lcv < 1000):
            break

    totalrev = str(round(Decimal(totalrev),2))



    return infodata,totalrev

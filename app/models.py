from app import app
from operator import itemgetter, attrgetter

class EthTokens(object):
    def __init__(self,symbol,name,tokenaddress,qty,price,value,sortval=0.0):
        self.symbol = symbol
        self.price = price
        self.name = name
        self.tokenaddress = tokenaddress
        self.qty = qty
        self.value = value
        self.sortval = 0.0
        
    def __iter__(self):
        return self

    def __repr__(self):
        return repr((self.tokenaddress,self.symbol,self.name,self.qty,self.price,self.value,self.sortval))
 
    def update(self,price,value,sortval):
        self.price = price
        self.value=value
        self.sortval=sortval
 

class BalancerInfo(object):
    def __init__(self,swapfee,rev,swapvol,userbalance,price,useradr,symbol,name,qty,poolid,totalshares,poolpct,tokenaddress,value):
        self.useradr = useradr
        self.symbol = symbol
        self.name = name
        self.qty = qty
        self.poolid = poolid
        self.userbalance = userbalance
        self.totalshares = totalshares
        self.rev = rev
        self.poolpct = poolpct
        self.tokenaddress = tokenaddress
        self.swapfee = swapfee
        self.swapvol = swapvol
        self.price = price
        self.value = value

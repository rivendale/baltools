from app import app

class EthTokens(object):
    def __init__(self,symbol,name,tokenaddress,qty):
        self.symbol = symbol
        self.name = name
        self.tokenaddress = tokenaddress
        self.qty = qty



class BalancerInfo(object):
    def __init__(self,swapfee,rev,swapvol,userbalance,useradr,symbol,name,qty,poolid,totalshares,poolpct,tokenaddress):
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
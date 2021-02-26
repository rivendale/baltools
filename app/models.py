from app import app


class BalancerInfo(object):
    def __init__(self,swapfee,rev,swapvol,userbalance,useradr,sym,name,qty,poolid,totalshares,poolpct,tokenaddress):
        self.useradr = useradr
        self.sym = sym
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
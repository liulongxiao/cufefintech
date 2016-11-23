from urllib.request import urlopen
import time
from tkinter.messagebox import  showerror,showinfo,showwarning

class listener:
    url=r'http://qt.gtimg.cn/q='
    def __init__(self,code,direction,price=None,pt_change=None,volumn=None):
        if price is None and pt_change is None and volumn is None:
            raise ValueError('price,volumn and pt_change cant be None the same time')
        self.direction=direction
        self.volumn=volumn
        self.hitDirection = direction
        self.stockId=code
        self.targetPrice=price
        self.targetPt_change=pt_change
        self._parse_open_data()
    def _parse_open_data(self):
        raw_data=urlopen(listener.url+self.stockId).read().decode('gbk')
        data=raw_data.split('|')[0].split('=')[1][1:].split('~')[1:]
        self.open=float(data[4])
        self.last_close=data[3]
        if self.targetPt_change:
            self.targetPriceCulculatedByChange=self.open*(1+self.targetPt_change/100)
        else:
            self.targetPriceCulculatedByChange=None
        print(self.targetPriceCulculatedByChange)
    def _run(self):
        try:
            raw_data = urlopen(listener.url + self.stockId,timeout=3).read().decode('gbk')
        except:
            time.sleep(3)
            return True
        data = raw_data.split('|')[0].split('=')[1][1:].split('~')[1:]
        print(float(data[2]))
        if self.volumn:
            if int(data[5])>self.volumn:
                showinfo('','股票{}目前价格{}达到了成交量{}的警戒线'.format(data[0],data[2],self.volumn))
                self.volumn=None
                return False
        if self.targetPrice:
            if self.direction==True:
                if float(data[2])>self.targetPrice:
                    showinfo('','股票{}目前价格{}涨到了价位{}的警戒线'.format(data[0],data[2],self.targetPrice))
                    self.targetPrice=None
                    return False
            if self.direction==False:
                if float(data[2])<self.targetPrice:
                    showinfo('','股票{}目前价格{}跌到了价位{}的警戒线'.format(data[0],data[2],self.targetPrice))
                    self.targetPrice=None
                    return False
        if self.targetPriceCulculatedByChange:
            if self.direction == True:
                if float(data[2]) > self.targetPriceCulculatedByChange:
                    print(data[2],self.targetPriceCulculatedByChange)
                    showinfo('', '股票{}目前价格{}达到了涨幅{}的警戒线'.format(data[0],data[2],self.targetPt_change))
                    self.targetPrice = None
                    return False
            if self.direction == False:
                if float(data[2]) < self.targetPriceCulculatedByChange:
                    showinfo('',  '股票{}目前价格{}达到了跌幅{}的警戒线'.format(data[0],data[2],self.targetPt_change))
                    self.targetPriceCulculatedByChange = None
                    return False
        return True

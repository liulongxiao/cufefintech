import urllib
import http.cookiejar
import lxml.etree
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#import crash_on_ipy
beginTime=datetime.datetime(2016,11,20,8,0)
list_time=[beginTime+datetime.timedelta(minutes=x) for x in range(850)]
sId=input('input the studentNum: ')
sPwd=input('input the password: ')

class student:
    def __init__(self,id,pwd):
        self.id=id
        self.pwd=pwd
    def getPostData(self):
        return urllib.parse.urlencode({'id':self.id,'pwd':self.pwd,'act':'login'}).encode()
class resv:
    def __init__(self,resv):
        self.over=resv.get('over')
        self.date=resv.get('date')
        self.tds=resv.xpath('tr[@class="content"]/td')
        self.name=self.tds[1].text
        self.beginTime = self.tds[3].xpath('div/div')[0].xpath('span')[1].text
        self.endTime=self.tds[3].xpath('div/div')[1].xpath('span')[1].text
        self.position=self.tds[0].xpath('div/a')[0].text
    def getBeginTime(self):
        z=self.beginTime
        return datetime.time(int(z[-5:-3]),int(z[-2:]))
    def getEndTime(self):
        z=self.endTime
        return datetime.time(int(z[-5:-3]),int(z[-2:]))
    def name(self):
        return self.name
    def position(self):
        return self.position


cookiejar =http.cookiejar.LWPCookieJar()
loginUrl=r'http://123.124.19.69/ClientWeb/pro/ajax/login.aspx'
cookie_support=urllib.request.HTTPCookieProcessor(cookiejar)
opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
urllib.request.install_opener(opener)
stu=student(sId,sPwd)

postData=stu.getPostData()
postHeader={
'Cookie':'{"ASP.NET_SessionId"="ftbfrxmldye2c2zgenvnyv45"}',
'Host':'123.124.19.69'
,'Origin':'http://123.124.19.69'
,'Referer':'http://123.124.19.69/ClientWeb/xcus/ic2/Default.aspx'
,'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
            }
req = urllib.request.Request(loginUrl, postData, postHeader)
response=urllib.request.urlopen(req)
res=urllib.request.urlopen(r'http://123.124.19.69/ClientWeb/xcus/a/center.aspx')
page=res.read()
page=page.decode()
tree=lxml.etree.HTML(page)
resvTable=tree.xpath('//table[@id="my_resv_tbl"]')[0]
resv_=resvTable.xpath('tbody')
resvs=list(map(resv,resv_))
def inTime(time_,resv):
    if time_<resv.getEndTime() and time_>resv.getBeginTime():
        return True
    else:
        return False
def timeanalyse(resvs,weekday):
    the_map={}
    for i in list_time:
        the_map[datetime.time(i.hour,i.minute)]=0
    for resv in resvs:
        date=datetime.datetime.strptime(resv.date[:10], '%Y-%m-%d')
        if date.weekday()==weekday-1 or True:
            for time_ in the_map.keys():
                if inTime(time_,resv):
                    the_map[time_]+=1
    return the_map
def seatanalyse(resvs):
    seat_map={}
    for resv in resvs:
        if resv.position not in seat_map.keys():
            seat_map[resv.position]=1
        else:
            seat_map[resv.position]+=1
    return seat_map
def timedelta(beginTime,endTime):
    btimes=datetime.datetime(2016,11,20,int(beginTime[-5:-3]),int(beginTime[-2:]))
    etimes=datetime.datetime(2016,11,20,int(endTime[-5:-3]),int(endTime[-2:]))
    times=etimes-btimes
    return  times.seconds/3600

def totalTime(resvs):
    timeSum=0
    for resv in resvs:
        timeDelta=timedelta(resv.beginTime,resv.endTime)
        timeSum+=timeDelta
    return timeSum
def change(s):
    return datetime.datetime(2016,11,20,s.hour,s.minute)
print(resvs[1].name)
plt.figure(figsize=(19, 16), dpi=100)
p=[]
for i in range(2)[1:]:
    p.append(plt.subplot(2,1,i))
    MAP=timeanalyse(resvs,i)
    y=[]
    x=[]
    for j in list_time:
        x.append(datetime.time(j.hour, j.minute))
        y.append(MAP[datetime.time(j.hour, j.minute)])
    x=list(map(change,x))
    p[i-1].plot(x, y, c='red')
p2=plt.subplot(2,1,2)

plt.title('total {} hours'.format(int(totalTime(resvs))))
#plt.show()
seat_map=seatanalyse(resvs)
df=pd.DataFrame(index=list(seat_map.keys()),data=list(seat_map.values()),columns=['number'])
df=df.loc[df.number>3]
x_label=np.array(list(enumerate(df.index)))
y_label=list(df.number)
p2.bar(left=list(map(int,x_label[:,0])),height=y_label,width = 0.2,tick_label=tuple(map(str,x_label[:,1])))
plt.show()



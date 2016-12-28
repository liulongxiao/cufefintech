import urllib
import http.cookiejar
import lxml.etree
import datetime
import re
import json
import pandas as pd
import matplotlib
#import crash_on_ipy
# position=input( '输入座位号')
class student:
    def __init__(self, id, pwd):
        self.id = id
        self.pwd = pwd

    def getPostData(self):
        return urllib.parse.urlencode({'id': self.id, 'pwd': self.pwd, 'act': 'login'}).encode()


accno=[]
name=[]
seats=[]
resvRequestUrl = r'http://123.124.19.69/ClientWeb/pro/ajax/device.aspx'
searchAccountUrl = r'http://123.124.19.69/ClientWeb/pro/ajax/data/searchAccount.aspx'
pattern = re.compile('roomId=(.+?)&')
room_map = {}
num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5}
studentId=input('input your studentId')
pwd=input('input your lib pwd')
stu = student(studentId,pwd )
postData = stu.getPostData()
postHeader = {
    'Cookie': '{"ASP.NET_SessionId"="ftbfrxmldye2c2zgenvnyv45"}',
    'Host': '123.124.19.69'
    , 'Origin': 'http://123.124.19.69'
    , 'Referer': 'http://123.124.19.69/ClientWeb/xcus/ic2/Default.aspx'
    ,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}
cookiejar = http.cookiejar.LWPCookieJar()
loginUrl = r'http://123.124.19.69/ClientWeb/pro/ajax/login.aspx'
cookie_support = urllib.request.HTTPCookieProcessor(cookiejar)
opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
urllib.request.install_opener(opener)
req = urllib.request.Request(loginUrl, postData, postHeader)
response = urllib.request.urlopen(req).read().decode()
response = urllib.request.urlopen(r'http://123.124.19.69/ClientWeb/xcus/ic2/Default.aspx').read().decode()
tree = lxml.etree.HTML(response)
rooms = tree.xpath('//ul[@class="it_cls_list nav"]')[0]
leaves = rooms.xpath('li')
for floor in leaves[1:]:
    rooms = floor.xpath('ul[@class="it_list sec_it_list nav"]/li')
    for room in rooms:
        roomId = pattern.findall(room.get('url'))[0]
        roomName = str(num_map[room.xpath('a/span')[0].text[0]]) + room.xpath('a/span')[0].text[2]
        room_map[roomName] = roomId
print('precess done')
for room in room_map.values():
    resvPostDataDict = {'byType': 'devcls',
                        'classkind': '8',
                        'display': 'fp',
                        'md': 'd',
                        'room_id': room,
                        'purpose': '',
                        'img': '../../upload/DevImg/FloorPlan/rm' +room+ '.jpg',
                        'cld_name': 'default',
                        'date': datetime.datetime.today().strftime('%F'),
                        'act': 'get_rsv_sta'}
    resvPostData = urllib.parse.urlencode(resvPostDataDict).encode()
    print(room)
    req = urllib.request.Request(resvRequestUrl, resvPostData, postHeader)
    page = urllib.request.urlopen(req).read().decode()
    jsonData = json.loads(page)
    for seat in jsonData['data']:
        if len(seat['ts']) == 0:
            continue
        if isinstance(seat['ts'][0]['owner'],list):
            print(seat['ts'][0]['owner'])
            continue
        name.append(seat['ts'][0]['owner'])
        accno.append(seat['ts'][0]['accno'])
        seats.append(seat['title'])


studentId=[]
institute=[]

accountHeader = {'Host': '123.124.19.69',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:49.0) Gecko/20100101 Firefox/49.0',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                 'Accept-Encoding': 'gzip, deflate',
                 'Upgrade-Insecure-Requests': '1',
                 'Connection': 'keep-alive'}
number=0
for seatOwner,seatOwnerId in zip(name,accno):
    raw_dict = {'term': seatOwner}
    try:
        nameReq = urllib.request.Request(searchAccountUrl, urllib.parse.urlencode(raw_dict).encode(), accountHeader)
    except:
        try:
            nameReq = urllib.request.Request(searchAccountUrl, urllib.parse.urlencode(raw_dict).encode(), accountHeader)
        except:
            studentId.append('dont Know')
            institute.append('dont Konw')
            continue
    accountInforms = json.loads(urllib.request.urlopen(nameReq).read().decode())
    Flag=False
    for accountInform in accountInforms:
        if accountInform['id'] == seatOwnerId:
            number+=1
            print(number,'total :',len(accno))
            studentId.append(accountInform['szLogonName'])
            institute.append(accountInform['label'])
            Flag=True
            break
    if not Flag:
        studentId.append('not Found')
        institute.append('not Found')
df=pd.DataFrame({'studentId':studentId,'name':name,'seat':seats,'institue':institute})
df['floor']=df.seat.str.slice(0,1).apply(int)
df['aera']=df.seat.str.slice(1,2)
df['institue']=df.institue.str.extract('.*\((.+)\).*')
gradeDict={1:'大一',2:'大二',3:'大三',4:'大四',5:'研一',6:'研二',100:'未知'}

def grade(x):
    if x[:5]=='20162':
        return 5
    if x[:5]=='20133':
        return 4
    if x[:5] == '20143':
        return 3
    if x[:5] == '20153':
        return 2
    if x[:5] == '20163':
        return 1
    if x[:5] == '20152':
        return 6
    else:
        return 100

def gradeIt(x):
    return gradeDict[x]
df['grade']=df.studentId.apply(grade)
df['grade']=df.grade.apply(gradeIt)
df.to_excel('libdata.xlsx')


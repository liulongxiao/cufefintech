import urllib
import pandas as pd
import sqlalchemy as scy
import json
import re
re_=re.compile(r'Class=(.+)')
SECID={'E':'stock','B':'bond','F':'fund','IDX':'theindex','FU':'futuer','OP':'option'}
def getData(api):
    url=r'https://api.wmcloud.com/data/v1'+api
    header={'Authorization': 'Bearer 9efa71a110cd2a0f5249a1e04ada74df5d2541e049cfa0d9cecf4dbaea4032c2'}
    page=urllib.request.Request(url,headers=header)
    result=urllib.request.urlopen(page).read().decode('utf-8')
    json_=json.loads(result)
    list=[]
    for i in range(len(json_['data'])):
        temp=pd.DataFrame.from_dict(json_['data'][i],orient='index')
        temp=pd.DataFrame(index=[i],data=temp.values.T,columns=temp.index)
        list.append(temp)
    df=pd.concat(list,axis=0)
    return df



api_=r'/api/master/getSecID.json?field=&ticker=&partyID=&assetClass='
api=[]
for i in ['E','B','F','IDX','FU','OP']:
    api.append(api_+i)


filename=r'C:\Users\llx\Desktop\logging.txt'
with open(filename,mode='a') as f:
    engine=scy.create_engine('mysql+pymysql://root:pwd@localhost/my?charset=utf8',echo=True)
    with engine.connect() as conn:
        for theapi in api:
            df=getData(theapi)
            df.to_sql(SECID[re_.findall(theapi)[0]]+'SECID',conn,chunksize=1000)


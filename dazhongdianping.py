from urllib.parse import urlencode,quote
from urllib.request import  urlopen,Request
import json
import pandas as pd
import lxml.etree
import http.cookiejar
import urllib
import re

not_find=re.compile('全站商户中，没有找到相应的商户')

cookiejar =http.cookiejar.LWPCookieJar()
cookie_support=urllib.request.HTTPCookieProcessor(cookiejar)
opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
urllib.request.install_opener(opener)

headers={
'Host':'www.dianping.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:49.0) Gecko/20100101 Firefox/49.0',
'Referer':'http://www.dianping.com/search/keyword/2/0_%E8%82%AF%E5%BE%B7%E5%9F%BA'
}

domain='http://www.dianping.com/search/keyword/'

def get_page(url):
    # headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    # 'Host':'www.dianping.com',
    # 'Upgrade - Insecure - Requests':'1'
    # }
    req=Request(url,headers=headers)
    res=urlopen(req).read()
    return res


def handle_entities(entities,cityname):
    df=pd.DataFrame(columns=['city','store_name','comment_num','stars','costs','situation'])
    for idx,entity in enumerate(entities):
        entity_name=entity.xpath('div[@class="txt"]/div[@class="tit"]/a')[0].xpath('h4')[0].text
        print(entity_name)
        entity_comment_num=entity.xpath('div[@class="txt"]/div[@class="comment"]/a/b')
        if len(entity_comment_num) == 0:
            entity_comment_num = 0
        else:
            entity_comment_num = entity_comment_num[0].text

        starts=entity.xpath('div[@class="txt"]/div[@class="comment"]/span')[0].get('title')
        costs=entity.xpath('div[@class="txt"]/div[@class="comment"]/a/b')
        if len(costs)==0:
            costs=None
        else:
            costs=costs[0].text
        situation=entity.xpath('div[@class="txt"]/div[@class="tit"]/span[@class="istopTrade"]')
        if len(situation)==0:
            situation='正常营业'
        else:
            situation=situation[0].text
        df.loc[str(idx)]=[cityname,entity_name,entity_comment_num,starts,costs,situation]
    return df


def get_city_page(citynum,keyword,page_num):
    url_=domain+str(citynum)+'/'+'0_'+quote(keyword)+'/p'+str(page_num)
    raw_pages=get_page(url_).decode()
    if not_find.search(raw_pages):
        print(page_num)
        return None
    tree=lxml.etree.HTML(raw_pages)
    city=tree.xpath('//a[@class="city J-city"]')[0]
    cityname=city.text
    entities=tree.xpath('//div[@class="shop-list J_shop-list shop-all-list"]/ul/li')
    return handle_entities(entities,cityname)


def get_city(citynum):
    df=[]
    for page_num in range(50):
        try:
            tmpdf=get_city_page(citynum,'肯德基',page_num)
        except urllib.error.HTTPError as e:
            print(page_num)
            break
        if tmpdf is None:
            break
        df.append(tmpdf)
    total_df=pd.concat(df,axis=0)
    return total_df
df=[]
for citynum in range(1,400):
    print(citynum)
    df.append(get_city(citynum))

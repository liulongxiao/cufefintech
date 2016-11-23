import json
import urllib
import pandas as pd
#import crash_on_ipy
root='zb'
#大的数据种类
main_map={'月度数据':'hgyd','季度数据':'hgjd','年度数据':'hgnd','分省月度':'fsyd','分省年度':'fsnd',
          '主要城市月度价格':'csyd','主要城市年度数据':'csnd'}

def iterDict(x):
    if isinstance(x,list):
        for i in x:
            for j in iterDict(i):
                yield j
    else:
        for i in x.keys():
            if isinstance(x[i],dict):
                for j in iterDict(x[i]):
                    yield j
            if isinstance(x[i],list):
                for j in iterDict(x[i]):
                    yield j
            yield i
#叶子节点树
class GovStatsLeaf:
    def __init__(self,dbcode,nodeId,name,queryUrl='http://data.stats.gov.cn/easyquery.htm'):
        self.nodeId=nodeId
        self.dbcode=dbcode
        self.name=name
        self.parsed=False
        self.queryUrl = queryUrl
        self.jsonData='hasn\'t been parsed'
        self.codeDict={}
        self.queryPostData='m=QueryData&dbcode=%s&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"zb","valuecode":"%s"}]&k1=1479304367084'
    def _parseData(self):
        if not self.parsed:
            self.postData= self.queryPostData%(self.dbcode,self.nodeId)
            request=urllib.request.Request(url=self.queryUrl,data=self.postData.encode())
            self.jsonData=json.loads(urllib.request.urlopen(request).read().decode())
            self.parsed=True
    def getJsonData(self):
        if not self.parsed:
            self._parseData()
        return self.jsonData
    def get_df(self):
        js=self.getJsonData()
        codeDf=pd.read_json(json.dumps(js['returndata']['wdnodes'][0]['nodes']))
        tempDict={}
        dataDf=pd.DataFrame()
        for data_ in js['returndata']['datanodes']:
            tempDict['data']=[data_['data']['data']]
            for wds in data_['wds']:
                tempDict[wds['wdcode']]=[wds['valuecode']]
            dataDf=pd.concat([dataDf,pd.DataFrame(data=tempDict)])
        #df=pd.merge(dataDf,codeDf,left_on='zb',right_on='code')

        return dataDf,codeDf
#根节点树
class GovStatsTree:
    def __init__(self,dbcode,name='root',root='zb',queryUrl='http://data.stats.gov.cn/easyquery.htm'):
        self.root=root
        self.queryUrl=queryUrl
        self.dbcode=dbcode
        if name=='root':
          self.name=main_map_inverse[dbcode]
        else:
          self.name=name
        self.postData={'id':self.root,
                'dbcode':dbcode,
                'wdcode':'zb',
                'm':'getTree'}
        self.leafChildren=[]
        self.treeChildren = []
        self.parsed=False
        self.jsonData='hasn\' been parsed'

    def _parseOneTime(self):
        if not self.parsed:
            postData_=urllib.parse.urlencode(self.postData)
            request=urllib.request.Request(url=self.queryUrl,data=postData_.encode())
            response=urllib.request.urlopen(request)
            page=response.read().decode()
            self.jsonData = json.loads(page)
            for i in self.jsonData:
                if i['isParent']:
                    self.treeChildren.append(GovStatsTree(dbcode=self.dbcode,root=i['id'],name=self.name+'-'+i['name']))
                else:
                    self.leafChildren.append(GovStatsLeaf(dbcode=self.dbcode,nodeId=i['id'],name=self.name+'-'+i['name']))
            self.parsed=True

    def getLeafChildren(self):
        if not self.parsed:
            self._parseOneTime()
        return self.leafChildren

    def getTreeChildren(self):
        if not self.parsed:
            self._parseOneTime()
        return self.treeChildren

    def allLeaves(self):
        for tree_son in self.getTreeChildren():
            for innerLeaf in allLeaves(tree_son):
                yield innerLeaf
        for leaf in self.getLeafChildren():
            yield leaf


#获取一棵树的所有叶子
def allLeaves(tree):
    for tree_son in tree.getTreeChildren():
        for innerLeaf in allLeaves(tree_son):
            yield innerLeaf
    for leaf in tree.getLeafChildren():
        yield leaf
leaves=[]
for key in main_map.keys():
    root=GovStatsTree(main_map[key])
    for leaf in root.allLeaves():
        leaves.append(leaf)


import urllib.request
import urllib.parse
import json


APPKEY='631c5a5b9992bd74'
API_URL='http://api.jisuapi.com/chengyu'
'''
        "name": "叶公好龙",
        "pronounce": "yè  gōng  hào  lóng",
        "content": "叶公：春秋时楚国贵族，名子高，封于叶（古邑名，今河南叶县）。比喻口头上说爱好某事物，实际上并不真爱好。",
        "comefrom": "汉·刘向《新序·杂事》记载：叶公子高非常喜欢龙，器物上刻着龙，房屋上也画着龙。真龙知道了，来到叶公家里，把头探进窗子。叶公一见，吓得拔腿就跑。",
        "antonym": [
            "名副其实",
            "名实相符"
        ],
        "thesaurus": [
            "表里不一",
            "言不由衷"
        ],
        "example": "1. 嘴里天天说,\"唤起民众\"，民众起来了又害怕得要死，这和叶公好龙有什么两样？"
-------------------------------------------
        没有找到数据返回-1
'''
def meaning(words=''):
    if words == '':
        return -1
    data = {}
    data['appkey'] = APPKEY
    data['chengyu']=words
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '/detail?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr= json.loads(result.read())
    res = jsonarr['result']
    if res:
        return {
            '名称':res['name'],
            '读音':res['pronounce'],
            '解释':res['content'],
            '出自':res['comefrom'],
            '反义词':','.join(res['thesaurus']) if len(res['thesaurus'])>1 else ''.join(res['thesaurus']),
            '近义词':','.join(res['antonym']) if len(res['antonym'])>1 else ''.join(res['antonym']),
            '举例':res['example'].replace(' ','')
        }
    else:
        return -1

def meaning1(words=''):
    if words == '':
        return -1
    data = {}
    data['appkey'] = APPKEY
    data['chengyu']=words
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '/detail?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr= json.loads(result.read())
    res = jsonarr['result']
    if res:
        return {
            'name':res['name'],
            'duyin':res['pronounce'],
            'jieshi':res['content'],
            'chuzi':res['comefrom'],
            'fanyici':','.join(res['thesaurus']) if len(res['thesaurus'])>1 else ''.join(res['thesaurus']),
            'jinyici':','.join(res['antonym']) if len(res['antonym'])>1 else ''.join(res['antonym']),
            'lizi':res['example'].replace(' ','')
        }
    else:
        return 0
'''
存在返回，
{'word1': '词严义正',
 'word2': '词言义正',
 'word3': '辞严义正',
 'word4': '义正词严',
 'word5': '义正辞严',
 'word6': '义正辞约'
}
不存在返回0

'''
def search(keyword=''):
    if keyword == '':
        return -1
    data = {}
    data['appkey'] = APPKEY
    data['keyword']=keyword
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '/search?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr= json.loads(result.read())
    res = jsonarr['result']
    if res:
        search_info = {}
        i = 1
        for item in res:
            search_info['word'+str(i)] = item['name']
            i += 1
        return search_info
    else:
        return -1

import urllib
import urllib.request
import urllib.parse
import json


def recommend(type='keji'):
    '''返回新闻列表'''
    APPKEY='279242fdf73bc44118057e142f81cabb'
    API_URL='http://v.juhe.cn/toutiao/index'
    data = {}
    data['key'] = APPKEY
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?type=' + type +'&'+ url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    if jsonarr['error_code'] != 0:
        print(jsonarr['reason'])
        exit()
    res = jsonarr['result']['data']
    news = []
    i = 0
    for new in res:
        resinfo = []
        resinfo.append(res[i]['title'])
        resinfo.append(res[i]['thumbnail_pic_s'])
        resinfo.append(res[i]['date'])
        news.append(resinfo)
        i += 1
    return news

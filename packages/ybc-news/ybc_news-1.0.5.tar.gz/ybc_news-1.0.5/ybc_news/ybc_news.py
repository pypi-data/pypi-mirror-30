import urllib
import urllib.request
import urllib.parse
import json
import re


def channels():
    '''获取新闻分类'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/news/channel'
    data = {}
    data['appkey'] = APPKEY
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        return res
    else:
        return -1

def news(channel='科技',num=10,start=0):
    '''获取指定分类下的新闻'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/news/get'
    data = {}
    data['appkey'] = APPKEY
    data['channel'] = channel
    data['num'] = num
    data['start'] = start
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res :
        news_list = []
        for item in res['list'] :
            res_info = []
            res_info.append(item['title'])
            res_info.append(item['time'])
            res_info.append(item['pic'])
            item['content'] = item['content'].replace('<br />','')
            dr = re.compile('<[^>]+>',re.S)
            item['content'] = dr.sub('',item['content']).strip()
            # res_info.append(item['content'])
            news_list.append(res_info)
        return news_list
    else :
        return -1


# def recommend(type='keji'):
#     '''返回新闻列表'''
#     APPKEY='279242fdf73bc44118057e142f81cabb'
#     API_URL='http://v.juhe.cn/toutiao/index'
#     data = {}
#     data['key'] = APPKEY
#     url_values = urllib.parse.urlencode(data)
#     url = API_URL + '?type=' + type +'&'+ url_values
#     result = urllib.request.urlopen(url)
#     jsonarr = json.loads(result.read())
#     if jsonarr['error_code'] != 0:
#         print(jsonarr['reason'])
#         exit()
#     res = jsonarr['result']['data']
#     news = []
#     i = 0
#     for new in res:
#         resinfo = []
#         resinfo.append(res[i]['title'])
#         resinfo.append(res[i]['thumbnail_pic_s'])
#         resinfo.append(res[i]['date'])
#         news.append(resinfo)
#         i += 1
#     return news

def main():
    # print(channels())
    print(news('军事',2))


if __name__ == '__main__':
    main()

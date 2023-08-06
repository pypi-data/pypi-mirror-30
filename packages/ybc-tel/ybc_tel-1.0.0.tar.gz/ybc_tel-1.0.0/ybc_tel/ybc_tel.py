import urllib.request
import urllib.parse
import json



def detail(tel=''):
    '''电话号详情'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/shouji/query'
    if tel == '':
        return -1
    data = {}
    data['appkey'] = APPKEY
    data['shouji'] = tel
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        res_info = {}
        res_info['province'] = res['province']
        res_info['city'] = res['city']
        res_info['company'] = res['company']
        res_info['phone'] = res['shouji']
        return res_info
    else:
        return -1

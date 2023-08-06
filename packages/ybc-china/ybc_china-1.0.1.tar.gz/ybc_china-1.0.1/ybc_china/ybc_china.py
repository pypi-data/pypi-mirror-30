import urllib.request
import urllib.parse
import json





def all_cities():
    '''获取所有城市'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/aqi/city'
    data = {}
    data['appkey'] = APPKEY
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        res_dict = []
        for item in res :
            res_dict.append(item['city'])
        return res_dict
    else:
        return -1

def _pros_info():
    '''获取所有省份'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/area/province'
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

def provinces():
    '''获取所有的省份'''
    res = _pros_info()
    prov_list = []
    if res != -1 :
        for item in res :
            prov_list.append(item['name'])
    return prov_list

def _get_parentid_by_proname(proname):
    res = _pros_info()
    if res != -1 :
        for item in res :
            if proname == item['name']:
                return item['id']

def cities(proname=''):
    '''根据省份获取城市'''
    if proname == '' :
        return -1
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/area/city'
    data = {}
    data['appkey'] = APPKEY
    pid = _get_parentid_by_proname(proname)
    data['parentid'] = pid
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res :
        city_list = []
        for item in res :
            city_list.append(item['name'])
        return city_list
    else:
        return -1




def main():
    print(provinces())
    print(cities('黑龙江省'))

if __name__ == '__main__':
    main()

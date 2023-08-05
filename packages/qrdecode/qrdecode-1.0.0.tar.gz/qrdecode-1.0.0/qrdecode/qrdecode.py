import urllib.request
import urllib.parse
import json
import base64


def decode(filename=''):
    '''
    正确返回结果，错误返回-1
    '''
    showapi_appid="53391"
    showapi_sign="890894ac7b444ff4baea4583a559ae5d"
    if filename == '':
        return -1
    f = open(filename,'rb')
    img_data = base64.b64encode(f.read()).decode('utf-8')
    f.close()
    url="http://route.showapi.com/887-4"
    send_data = urllib.parse.urlencode([
        ('showapi_appid', showapi_appid)
        ,('showapi_sign', showapi_sign)
                        ,('imgData', img_data)
                        ,('handleImg', "")

    ])
    req = urllib.request.Request(url)
    try:
           response = urllib.request.urlopen(req, data=send_data.encode('utf-8'), timeout = 10) # 10秒超时反馈
    except Exception as e:
        print(e)
    result = response.read().decode('utf-8')
    result_json = json.loads(result)
    if result_json['showapi_res_body']['ret_code'] == 0:
        return result_json['showapi_res_body']['retText']
    else:
        return -1

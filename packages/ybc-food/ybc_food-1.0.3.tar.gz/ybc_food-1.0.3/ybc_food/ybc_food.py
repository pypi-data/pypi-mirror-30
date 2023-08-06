import requests
import json
import base64
import os
import math
import sys

def check(filename=''):
    '''美食图片检测'''
    if not filename:
        return False

    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/imgFoodCheck.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data'] :
        res['data']['confidence'] = str(math.ceil(res['data']['confidence']*100)) + '%'
        return res['data']['food']
    else:
        return False


def _get_access_token():
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/aniToken.php'
    r = requests.post(url)
    res = r.json()
    return res['access_token']

'''食物识别'''
def food(filename='', topNum=3):
    if not filename:
        return -1
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/imgFood.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['access_token'] = _get_access_token()
    data['topNum'] = topNum
    r = requests.post(url, data=data)
    res = r.json()
    if res['result'] :
        if topNum == 1:
            return res['result'][0]
        else:
            return res['result']

def main():
    res = food('1.jpg')
    print(res)
    res = food('2.jpg',5)
    print(res)
    res = check('2.jpg')
    print(res)
if __name__ == '__main__':
    main()

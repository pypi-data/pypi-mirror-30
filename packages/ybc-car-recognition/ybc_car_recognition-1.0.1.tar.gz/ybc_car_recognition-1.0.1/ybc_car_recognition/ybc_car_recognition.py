import requests
import json
import base64
import os

def recognize(filename=''):
    '''车品牌识别'''
    if not filename:
        return -1

    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/imgCar.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res = res['data']['tag_list'][0]
        return res['label_name']
    else:
        return -1

def main():
    res = recognize('1.jpeg')
    print(res)
if __name__ == '__main__':
    main()

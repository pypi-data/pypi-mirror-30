import requests
import json
import base64
import os

def car_recognition(filename=''):
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
        return res['data']['tag_list'][0]['label_name']
    else:
        return '车辆识别错误~'

def main():
    res = car_recognition('1.jpeg')
    print(res)
if __name__ == '__main__':
    main()

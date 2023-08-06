import requests
import json
import base64
import os


def general_info(filename=''):
    '''通用文字识别'''
    if not filename:
        return -1

    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/generalOcr.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res_list = []
        for val in res['data']['item_list'] :
            res_list.append(val['itemstring'])
        return res_list
    else:
        return -1


def main():
    res = general_info('1.jpg')
    print(res)

if __name__ == '__main__':
    main()

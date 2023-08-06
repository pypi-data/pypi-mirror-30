import requests
import json
import base64
import os


def driver_info(filename='', dtype=0):
    '''驾驶证,行驶证识别,type:0代表行驶证,1代表驾驶证'''
    if not filename :
        return -1
    if dtype not in (0,1) :
        return -1
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/driverLicenseOcr.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['type'] = dtype
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res_dict = {}
        for val in res['data']['item_list'] :
            res_dict[val['item']] = val['itemstring']
        return res_dict
    else:
        return -1


def main():
    res = driver_info('card1.jpg',0)
    print(res)
    # res = driver_info('card2.jpg',1)
    # print(res)



if __name__ == '__main__':
    main()

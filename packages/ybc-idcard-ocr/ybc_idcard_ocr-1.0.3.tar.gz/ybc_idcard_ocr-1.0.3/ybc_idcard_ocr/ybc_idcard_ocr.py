import requests
import json
import base64
import os
import cv2
import time
from PIL import Image

def camera():
    cap = cv2.VideoCapture(0)
    while(1):
        ret, frame = cap.read()
        cv2.imshow("capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            now = time.localtime()
            filename = str(now.tm_year) + str(now.tm_mon) + str(now.tm_mday) + str(now.tm_hour) + str(now.tm_min) + str(now.tm_sec) + '.jpg'
            cv2.imwrite(filename, frame)
            break
    cap.release()
    cv2.destroyAllWindows()
    return filename

def idcard_info(filename='', card_type=0):
    '''身份证识别，card_type:0代表正面，1代表反面'''
    if not filename :
        return -1
    if card_type not in (0,1) :
        return -1
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/idCardOcr.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['card_type'] = card_type
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        del res['data']['frontimage']
        del res['data']['backimage']
        del res['data']['authority']
        del res['data']['valid_date']
        return res['data']
    else:
        return -1


def main():
    res = idcard_info('card0.jpg')
    print(res)
    res = idcard_info('card1.jpg',1)
    print(res)



if __name__ == '__main__':
    main()

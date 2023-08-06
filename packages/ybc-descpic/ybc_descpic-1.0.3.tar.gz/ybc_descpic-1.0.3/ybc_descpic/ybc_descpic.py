import requests
import json
import os
import base64
from PIL import Image

def _resize_img(filepath,max_size=512000):
    # MAX_FILE_SIZE = max_size
    filesize = os.path.getsize(filepath)
    # if filesize > MAX_FILE_SIZE :
    im = Image.open(filepath)
    src_w = im.size[0]
    src_h = im.size[1]
    dst_w = 360
    dst_h = (src_h/src_w) * 360
    dst_size = dst_w , dst_h
    im.thumbnail(dst_size)
    im.save(filepath)
    return filepath

def desc(filename=''):
    '''描述图片'''
    API_URL = 'https://www.yuanfudao.com/tutor-ybc-course-api/pictalk.php'
    if not filename:
        return -1
    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img']=b64img
    r = requests.post(API_URL, data=data)
    res = r.json()
    if res['ret'] == 0:
        return res['data']['text']
    else:
        return -1

def main():
    res = desc('1.jpg')
    print(res)

if __name__ == '__main__':
    main()

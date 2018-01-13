from aip import AipOcr
import time
import json
from PIL import Image
import requests
import os
import itchat
import traceback


class AutoAnswer:
    APP_KEY = "your_app_key"
    APP_ID = "your_app_id"
    SECRET_KEY = "your_secret_key"
    client = AipOcr(APP_ID, APP_KEY, SECRET_KEY)
    width, height = 0, 0
    # 在下面填入想要自动发送微信的好友微信号/昵称/备注
    users = []

    @classmethod
    def adb_connect(cls):
        # 网易mumu的端口号是5555，如果连接自己的手机则不需要此函数
        os.system('adb connect 127.0.0.1:5555')

    @classmethod
    def adb_get_image(cls, filepath):
        os.system('adb shell /system/bin/screencap -p /sdcard/screenshot.png')
        os.system('adb pull /sdcard/screenshot.png ./' + filepath)

    @classmethod
    def detect_question(cls, filepath):
        im = Image.open(filepath)
        global width
        global height
        width, height = im.size
        # 不同机型对应的line不同，例如三星S7对应为330
        line = [100 * width // 1080, 220 * height // 1920, 900 * width // 1080, 220 * height // 1920]
        is_question = True
        for x in range(line[0], line[2]):
            if len(set(im.getpixel((x, line[1]))) - {255}) != 0:
                is_question = False
        return is_question, im

    @classmethod
    def cut_image(cls, im):
        width, height = im.size
        box = 0, 120 * height // 1920, 1080 * width // 1080, 1400 * height // 1920
        print("box", box)
        region = im.crop(box)
        region.save('m3.png', 'PNG')

    @classmethod
    def get_file_content(cls, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    @classmethod
    def get_result(cls, res, question, options):
        print("get_result options", options)
        # 如果在服务器上运行MillionareHero.py，请将下面url替换
        url = "http://localhost:8995/m/"

        payload = json.dumps({'question': question, 'options': options})
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        data = json.loads(response.text)
        print("data", data)
        privative = {'不是', '不属于', '没有', '不包括', '不在', '不包含'}
        reverse = False
        for item in privative:
            if item in question:
                reverse = True
        print("reverse", reverse)
        if reverse:
            result = res[data[len(data) - 1][0]]
        else:
            result = res[data[0][0]]
        print("result", result)
        top = result['location']['top'] + 120 * height // 1920
        print('adb shell input tap %s %s' % (250, top))
        # 自动点击，如果不需要可以去掉
        os.system('adb shell input tap %s %s' % (250, top))

        return result['words']

    @classmethod
    def get_detail(cls, res):
        words_result = res['words_result']
        words_result = sorted(words_result, key=lambda x: x['location']['top'])
        question = ''
        options = dict()
        is_question = True
        order = ['A', 'B', 'C', 'D', 'E']
        for item in words_result:
            if is_question:
                question += item['words']
                if question.endswith('?') or question.endswith('？'):
                    is_question = False
            else:
                options[order[0]] = item
                order = order[1:]
        return question[2:], options

    @classmethod
    def notice_users(cls, text):
        for user in cls.users:
            username = itchat.search_friends(name=user)[0]['UserName']
            itchat.send(text, toUserName=username)
            print('send', text, ' to', user)

    @classmethod
    def auto_start(cls):
        cls.adb_connect()
        itchat.auto_login(True)
        while True:
            try:
                start_time = time.time()
                cls.adb_get_image('m2.png')
                is_question, im = cls.detect_question('m2.png')
                print("检测到问题？", is_question)
                if not is_question:
                    time.sleep(1)
                    continue
                else:
                    cls.cut_image(im)
                    image = cls.get_file_content("m3.png")
                    res = cls.client.general(image)

                    print(res)
                    question, options = cls.get_detail(res)
                    print("解析图片耗时", time.time() - start_time)
                    print(question)
                    print(options)
                    result = cls.get_result(options, question, {x: options[x]['words'] for x in options})
                    print(result)
                    cls.notice_users(result)
                    print("共耗时", time.time() - start_time)
                    time.sleep(30)
            except Exception as e:
                traceback.print_exc()
                # cls.notice_users('出错了...')
            finally:
                time.sleep(1)


AutoAnswer.auto_start()

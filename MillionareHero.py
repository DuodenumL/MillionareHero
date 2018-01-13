# coding=utf-8
import json
from bs4 import BeautifulSoup
import jieba
from jieba import analyse
import time
import aiohttp
from aiohttp import web
import asyncio

GOOGLE = {"url": "https://www.google.com/search?q=", "content_id": "ires"}
BAIDU = {"url": "https://www.baidu.com/s?wd=", "content_id": "content_left"}

privative = {'不是', '不属于', '没有', '不包括', '不包含'}
rm = {'不', '没'}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/63.0.3239.84 Safari/537.36"
}


class MillionareHero:

    def __init__(self, question, options, engine=BAIDU):
        self.score = {k: 0 for k in options}
        self.options = options
        self.seg_question = MillionareHero.get_keyword(question) - privative
        for item in rm:
            question = question.replace(item, '')
        self.seg_question.add(question)
        self.question = ' '.join(self.seg_question)
        self.engine = engine
        print(self.question)

    async def get_score(self):
        tasks = [asyncio.ensure_future(self.search_question(self.question, self.options, self.engine))]
        for option in self.options.items():
            tasks.append(asyncio.ensure_future(self.search_option(self.seg_question, option, self.engine)))
        await asyncio.gather(*tasks)
        return self.score

    async def search_option(self, seg_question, option, engine=BAIDU):
        print("抓取选项中...", option)
        t1 = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(engine['url'] + option[1], headers=headers) as resp:
                html = await resp.text()
                # html = bytearray(html.content).decode("utf-8")
                html = BeautifulSoup(html, 'html.parser').find('div', attrs={'id': engine['content_id']}).getText()
                print(option)
                self.score[option[0]] += MillionareHero.get_score_from_option(html, seg_question)
                print("抓完了", option, time.time() - t1)

    async def search_question(self, question, options, engine=BAIDU):
        print("抓取问题中...", question)
        t1 = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(engine['url'] + question, headers=headers) as resp:
                html = await resp.text()
                # html = bytearray(html.content).decode("utf-8")
                html = BeautifulSoup(html, 'html.parser').find('div', attrs={'id': engine['content_id']}).getText()
                # print("html", html)

                score_from_question = MillionareHero.get_score_from_question(html, options)
                print(score_from_question)
                for k in score_from_question:
                    self.score[k] += score_from_question[k]
                print("抓完了...", question, time.time() - t1)

    @staticmethod
    def cut(string):
        return set(jieba.cut_for_search(string, HMM=True))

    @staticmethod
    def get_keyword(string):
        return set(analyse.tfidf(string))

    @staticmethod
    def get_score_from_question(html, options):
        result = {k: 0 for k in options}
        positions = {k: html.count(options[k]) for k in options}
        sorted_positions = sorted(positions.items(), key=lambda x: x[1])
        for i, v in enumerate(sorted_positions):
            if v[1] != 0:
                result[v[0]] += i * 20
        return result

    @staticmethod
    def get_score_from_option(html, seg_question):
        cnt = 0

        for q in seg_question:
            if html.find(q) >= 0:
                cnt += 1
                print(q)
        print(cnt / len(seg_question) * 50)
        return cnt / len(seg_question) * 50


async def get_handler(request):
    start_time = time.time()
    data = await request.json()
    # 如果具备条件，可以将engine换为Google
    m = MillionareHero(data['question'], data['options'], engine=BAIDU)
    score = await m.get_score()
    response = "%s" % json.dumps(sorted(score.items(), key=lambda x: x[1], reverse=True))
    print("共耗时", time.time() - start_time)

    return web.Response(body=response.encode('utf-8'))


async def start(loop):
    app = web.Application(loop=loop)
    app.router.add_post('/m/', get_handler)
    # web.run_app(app, host='0.0.0.0', port=8995)
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 8995)
    print('Server started at http://127.0.0.1:8995...')
    return srv


if __name__ == "__main__":
    jieba.load_userdict('dict.big.txt')
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(loop))
    loop.run_forever()

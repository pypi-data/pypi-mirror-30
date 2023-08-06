# -*- codding: utf-8 -*-
from threading import Thread
import hashlib
import time
import re
import os

from fake_useragent import UserAgent
import lxml.html
import asyncio
import aiohttp


class Pump(Thread):
    def __init__(self, pages, selector, path='output'):
        Thread.__init__(self)

        self._start = time.time()

        self.pages = pages
        self.selector = selector
        self.path = path

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.headers = {'User-Agent': UserAgent().chrome}


    def correct(self, url):
        return url


    def hashname(self, url):
        name = hashlib.md5(url.encode()).hexdigest()
        ext = url.split('.')[-1]
        return os.path.join(self.path, f'{name}.{ext}')


    async def scraping(self, session, queue, urls):
        for url in urls:
            async with session.get(url) as response:
                text = await response.read()
                html = lxml.html.fromstring(text)

                for url in html.xpath(f'.//img[@class="{self.selector}"]/@src'):
                    await queue.put(self.correct(url))

        await queue.put(None)


    async def downloads(self, session, queue):
        while True:
            url = await queue.get()

            if url is not None:
                async with session.get(url) as response:
                    with open(self.hashname(url), 'wb') as file:
                        content = await response.read()
                        file.write(content)
                        print(url)
            else:
                break


    async def session(self, queue):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = list()
            for urls in self.pages:
                tasks.append(asyncio.ensure_future(self.scraping(session, queue, urls)))
                tasks.append(asyncio.ensure_future(self.downloads(session, queue)))

            responses = await asyncio.gather(*tasks)


    def run(self):
        loop = asyncio.get_event_loop()

        queue = asyncio.Queue(loop=loop)
        future = asyncio.ensure_future(self.session(queue))

        loop.run_until_complete(future)
        loop.close()


    def __del__(self):
        total = int(time.time() - self._start)
        minutes = total // 60
        seconds = total % 60

        if minutes:
            print(f'time - {minutes}m {seconds}s')
        else:
            print(f'time - {seconds}s')


if __name__ == '__main__':
    print("module pump")

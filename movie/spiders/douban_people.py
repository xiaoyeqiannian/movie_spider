import scrapy
import json
import re
from movie.items import People
from lxml import etree
from urllib.parse import unquote


class DoubanPeopleSpider(scrapy.Spider):
    name = 'douban_people'
    start_urls = []
    for item in ["凉面"]:
        start_urls.append("https://www.douban.com/j/search?cat=1005&q={0}&start=0".format(item))

    def parse(self, response):
        print(response.url)
        _key = re.findall(r'q=(.*)\&', unquote(response.url))
        ret = json.loads(response._body)
        if not ret.get('items'):
            return

        html = etree.HTML(''.join(ret['items']))
        searched = html.xpath('////div[@class="content"]/div/h3/a')
        print(len(searched))
        if not searched:
            return
        
        for item in searched:
            name = item.xpath("text()")[0]
            if _key and name != _key[0]:
                continue

            url = item.xpath("@href")
            if not url:
                continue

            url = unquote(url[0])
            people = re.findall(r'people/(.*)/', url)
            if people:
                yield scrapy.Request("https://movie.douban.com/people/{}/collect".format(people[0]),
                                callback=self.collect,
                                meta={'id': people[0]})
        r = re.findall(r'.*start=(\d+)', response.url)
        r = r and int(r[0]) or 0
        r += 20
        url = re.sub(r'start=\d+', 'start='+str(r), response.url, 1)
        yield scrapy.Request(url,
                            callback=self.parse,
                            meta={})
    
    def collect(self, response):
        items = response.xpath('//div[@class="item"]/div/a')
        print(response.meta.get('id'),'看过',len(items))
        for item in items:
            href = item.xpath('@href').get()
            if not href:
                continue

            # print('27195078', href)
            if '27195078' in href:
                _id = response.xpath('//div[@id="db-usr-profile"]/div/a/@href').get()
                print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<',_id)
                self.crawler.engine.close_spider(self, '')
                return _id

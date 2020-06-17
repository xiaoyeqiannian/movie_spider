import scrapy
import json
import re
from lxml import etree
from movie.items import Info1


class EndataSpider(scrapy.Spider):
    name = 'endata'
    URL = 'http://www.endata.com.cn/API/GetData.ashx'
    def __init__(self, name=None, **kwargs):
        pass

    def start_requests(self):
        for y in range(1990, 2020):
            yield scrapy.FormRequest(
                    url=self.URL,
                    formdata={
                        'areaId': '50',
                        'typeId': '4',
                        'year':  str(y),
                        'pageIndex': '1',
                        'pageSize': '20',
                        'MethodName': 'BoxOffice_GetMovieData_List',
                    },
                    meta={'pageIndex': 1, 'year': y},
                    callback=self.parse)

    def parse(self, response):
        ret = json.loads(response._body)
        print(response.url, response.meta, ret['Data']['Table1'])
        for item in ret['Data']['Table']:
            response.meta['box_office'] = item.get('amount')
            response.meta['code'] = item.get('ID')
            response.meta['name'] = item.get('MovieName')
            response.meta['page'] = response.meta.get('pageIndex')
            response.meta['country'] = '中国'
            yield scrapy.FormRequest(
                    url="http://www.endata.com.cn/API/GetData.ashx",
                    formdata={
                        'movieId': str(item.get('ID')),
                        'MethodName': 'BoxOffice_GetMovieData_Details'
                    },
                    meta=response.meta,
                    callback=self.endata_movie_show)
            
        total_page = ret['Data']['Table1'][0]['TotalPage']
        if response.meta['pageIndex']+1 <= total_page:
            yield scrapy.FormRequest(
                    url=self.URL,
                    formdata={
                        'areaId': '50',
                        'typeId': '4',
                        'year':  str(response.meta['year']),
                        'pageIndex': str(response.meta['pageIndex']+1),
                        'pageSize': '20',
                        'MethodName': 'BoxOffice_GetMovieData_List',
                    },
                    meta={'pageIndex': response.meta['pageIndex']+1, 'year': response.meta['year']},
                    callback=self.parse)
        
    def endata_movie_show(self, response):
        ret = json.loads(response._body)
        if len(ret['Data']['Table']) > 0:
            response.meta['show_time'] = ret['Data']['Table'][0].get('ReleaseTime')
            response.meta['releaser'] = ret['Data']['Table'][0].get('MovieFxAll')
            response.meta['producter'] = ret['Data']['Table'][0].get('MovieZz')
            yield scrapy.Request('https://m.douban.com/search/?query={}'.format(response.meta['name']),
                                    callback=self.spider_douban_search,
                                    meta=response.meta)

    def spider_douban_search(self, response):
        for i,v in enumerate(response.xpath('//ul[@class="search-results"]/li')):
            kind = v.xpath('span/text()').get()
            if kind != '影视':
                continue

            ul = v.xpath('ul/li/a/@href').getall()
            if not ul:
                continue

            code = re.findall(r'/movie/subject/(\d+)/', ul[0])
            # print(code)
            if not code:
                continue

            dbname = v.xpath('ul/li/a/div/span/text()').getall()
            response.meta['dbname'] = dbname and dbname[0]
            yield scrapy.Request('https://movie.douban.com/subject/{}/'.format(code[0]),
                                callback=self.spider_video_online,
                                meta=response.meta)

    def spider_video_online(self, response):
        online = response.xpath('//div[@class="gray_ad"]/ul/li/a/@data-cn').getall()
        yield Info1(id = response.meta.get('code'),
                    country = response.meta.get('country'),
                    page = response.meta.get('pageIndex'),
                    name = response.meta.get('name'), # 影片名称
                    dbname = response.meta.get('dbname'), # 影片名称
                    producter = response.meta.get('producter'), # 出品公司
                    releaser = response.meta.get('releaser'), # 发行公司
                    show_time = response.meta.get('show_time'), # 公映日期
                    box_office = response.meta.get('box_office'), # 总票房
                    video_online = online and ','.join(online) or '')

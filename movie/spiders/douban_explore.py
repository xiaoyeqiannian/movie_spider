import scrapy
import json
import re
from movie.items import Info1
from lxml import etree


class DoubanExploreSpider(scrapy.Spider):
    name = 'douban_explore'
    start_urls = ['https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%8A%A8%E7%94%BB&sort=time&page_limit=20&page_start=0']

    def parse(self, response):
        print(response.url)
        ret = json.loads(response._body)
        if not ret.get('subjects'):
            return

        r = re.findall(r'.*page_start=(\d+)', response.url)
        for item in ret['subjects']:
            yield scrapy.Request(item.get('url'),
                                callback=self.film_detail,
                                meta={'name': item['title'], 'page': r and r[0] or '0'})
        
        r = r and int(r[0]) or 0
        r += 20
        url = re.sub(r'page_start=\d+', 'page_start='+str(r), response.url, 1)
        response.meta['page'] = str(r)
        yield scrapy.Request(url,
                            callback=self.parse,
                            meta=response.meta)
    
    def film_detail(self, response):
        online = response.xpath('//div[@class="gray_ad"]/ul/li/a/@data-cn').getall()
        release_date = response.xpath('//*[@id="info"]/span[@property="v:initialReleaseDate"]/text()').getall()
        release_date = release_date and ' '.join(release_date)
        release_date = release_date and re.findall(r'\d{4}-\d{2}-\d{2}', release_date)
        info = response.xpath('//*[@id="info"]').get()
        country = re.findall('<span class="pl">制片国家/地区:</span> (.*)<br>', info)

        response.meta['country'] = country and country[0].strip() or ''
        response.meta['video_online'] = online and ','.join(online) or ''
        response.meta['show_time'] = release_date and release_date[0] or '-'
        yield scrapy.FormRequest(
                    url="http://www.endata.com.cn/API/GetData.ashx",
                    formdata={
                        'keyword': response.meta['name'],
                        'MethodName': 'BoxOffice_SearchAll'
                    },
                    meta=response.meta,
                    callback=self.endata_search)


    def endata_search(self, response):
        ret = json.loads(response._body)['Data']['Table']
        to_detail = False
        if len(ret) > 0:
            for i in ret:
                if response.meta['name'] in (i['enname'], i['cnname']) and response.meta['show_time'].split('-')[0]==i['releaseYear']:
                    to_detail = True
                    yield scrapy.FormRequest(
                        url="http://www.endata.com.cn/API/GetData.ashx",
                        formdata={
                            'movieId': str(i.get('id')),
                            'MethodName': 'BoxOffice_GetMovieData_Details'
                        },
                        meta=response.meta,
                        callback=self.endata_movie_show)
                    break

        if not to_detail:
            yield Info1(id = response.meta.get('code'),
                country = response.meta.get('country'),
                name = response.meta.get('name'), # 影片名称
                producter = '', # 出品公司
                releaser = '', # 发行公司
                show_time = response.meta.get('show_time'), # 公映日期
                box_office = response.meta.get('box_office'), # 总票房
                video_online = response.meta.get('video_online'))



    def endata_movie_show(self, response):
        ret = json.loads(response._body)
        yield Info1(id = response.meta.get('code'),
                page = response.meta.get('page'),
                country = response.meta.get('country'),
                name = response.meta.get('name'), # 影片名称
                producter = len(ret['Data']['Table']) > 0 and ret['Data']['Table'][0].get('MovieZz'), # 出品公司
                releaser = len(ret['Data']['Table']) > 0 and ret['Data']['Table'][0].get('MovieFxAll'), # 发行公司
                show_time = response.meta.get('show_time'), # 公映日期
                box_office = len(ret['Data']['Table']) > 0 and str(ret['Data']['Table'][0].get('SumBoxOffice'))+'万', # 总票房
                video_online = response.meta.get('video_online'))
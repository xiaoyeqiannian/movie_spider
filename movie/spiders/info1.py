import scrapy
import re
import json
from lxml import etree
from movie.items import Info1

class Info1Spider(scrapy.Spider):
    name = 'info1'
    start_urls = []
    countrys = {'2':'大陆','3':'美国','7':'韩国','6':'日本','10':'中国香港','13':'中国台湾','9':'泰国','8':'印度','4':'法国','5':'英国','14':'俄罗斯','16':'意大利','17':'西班牙','11':'德国','19':'波兰','20':'澳大利亚','21':'伊朗','100':'其他'}

    def __init__(self, name=None, **kwargs):
        super(Info1Spider, self).__init__(name, **kwargs)

        # for i in range(13):
            # for k,v in self.countrys.items():
            #     self.start_urls.append('https://maoyan.com/films?catId=4&yearId={0}&sourceId={1}&showType=3'.format(14, k))
        self.start_urls.append('https://maoyan.com/films?catId=4&yearId={0}&sourceId={1}&showType=3'.format(14, 2))
        # self.start_urls = self.start_urls[:1]# for test

    def parse(self, response):
        c = re.findall(r'.*sourceId=(\d+)&.*', response.url)
        p = re.findall(r'.*offset=(\d+)$', response.url)
        for i,v in enumerate(response.xpath('//div[@class="channel-detail movie-item-title"]')):
            name = v.xpath('a/text()').get()
            url = v.xpath('a/@href').get()
            code = re.findall(r'/films/(\d+)$', url)
            if not code:
                continue

            # print(response.url,i, c, p,name, url, code)
            response.meta['code'] = code[0]
            response.meta['name'] = name
            response.meta['page'] = p and 1+int(p[0])/30 or '1'
            response.meta['country'] = c and self.countrys.get(c[0]) or ''
            yield scrapy.Request('http://piaofang.maoyan.com/movie/{}/moresections'.format(code[0]),
                                callback=self.spider_moresections,
                                meta=response.meta)
        if 'offset' not in response.url:
            page = response.xpath('//ul[@class="list-pager"]/li')
            if page and len(page)>1:
                m_page = page[-2].xpath('a/text()').get()
                if m_page and m_page.isdigit():
                    for i in range(int(m_page))[1:]:
                        # print(response.url+'&offset='+str(i*30))
                        yield scrapy.Request(response.url+'&offset='+str(i*30),
                                    callback=self.parse,
                                    meta=response.meta)

    def spider_moresections(self, response):
        ret = json.loads(response._body)
        sectionHTMLs = ret.get('sectionHTMLs')
        if sectionHTMLs:
            companySection = sectionHTMLs.get('companySection')
            companySection = companySection and companySection.get('html') or ''
            if companySection:
                html = etree.HTML(companySection)
                for i,v in enumerate(html.xpath('//div[@class="category"]')):
                    sub = v.xpath('div[@class="cat-header"]/h2/text()')
                    com = v.xpath('div[@class="items"]/div/p/text()')
                    if '发行' in sub:
                        response.meta['releaser'] = ','.join(com)
                        # print(response.url,sub, com)
                    elif '出品' in sub:
                        response.meta['producter'] = ','.join(com)
                        # print(response.url,sub, com)

        yield scrapy.Request('http://piaofang.maoyan.com/movie/{}/boxshow'.format(response.meta['code']),
                                callback=self.spider_piaofang,
                                meta=response.meta)

    def spider_piaofang(self, response):  
        show_time = response.xpath('//div[@class="info-detail-title"]/div[@class="info-etitle-bar"]/text()').get()
        box_office = response.xpath('//div[@class="box-summary"]/div/p/span/text()').getall()
        box_office = box_office and len(box_office)>1 and box_office[0]+box_office[1] or '-'
        response.meta['show_time'] = show_time
        response.meta['box_office'] = box_office
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
                    page = response.meta.get('page'),
                    name = response.meta.get('name'), # 影片名称
                    dbname = response.meta.get('dbname'), # 影片名称
                    producter = response.meta.get('producter'), # 出品公司
                    releaser = response.meta.get('releaser'), # 发行公司
                    show_time = response.meta.get('show_time'), # 公映日期
                    box_office = response.meta.get('box_office'), # 总票房
                    video_online = online and ','.join(online) or '')


import scrapy
import re
from movie.items import MovieItem
from movie.items import ArtistItem
from movie.items import TrailerItem
from movie.items import PicItem

class DoubanSpider(scrapy.Spider):
    
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/coming']

    def parse(self, response):
        url_list = response.xpath('//*[@id="content"]/div/div[1]/table/tbody/tr/td[2]/a/@href').getall()
        title_list = response.xpath('//*[@id="content"]/div/div[1]/table/tbody/tr/td[2]/a/text()').getall()
        release_date_list = response.xpath('//*[@id="content"]/div/div[1]/table/tbody/tr/td[1]/text()').getall()
        for i in range(len(release_date_list)):
            release_date_list[i] = release_date_list[i].replace(' ', '').replace('\n', '')
        for i in range(len(title_list)):
            yield scrapy.Request(url_list[i], callback=self.spider_douban_movie)


    def spider_douban_movie(self, response):
        name = response.xpath('//*[@id="content"]/h1/span[1]/text()').get()
        name = name.split(' ')[0].encode('utf-8')
        if not name:
            return

        rating = response.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()').get()

        kind = response.xpath('//*[@id="info"]/span[@property="v:genre"]/text()').getall()
        kind = '/'.join(kind)

        duration = response.xpath('//*[@id="info"]/span[@property="v:runtime"]/text()').get()
        duration = duration and re.findall(r'(\d*)分钟', duration)[0]

        release_date = response.xpath('//*[@id="info"]/span[@property="v:initialReleaseDate"]/text()').get()
        showdate = release_date and re.findall(r'\d{4}-\d{2}-\d{2}', release_date)[0]

        info = response.xpath('//*[@id="info"]').get()
        language = re.findall('<span class="pl">语言:</span>(.*)<br>', info)
        language = language and language[0].strip() or ''

        country = re.findall('<span class="pl">制片国家/地区:</span> (.*)<br>', info)
        country = country and country[0].strip() or ''

        alternate_name = re.findall('<span class="pl">又名:</span> (.*)<br>', info)
        alternate_name = alternate_name and alternate_name[0].strip() or ''

        synopsis = response.xpath('//*[@id="link-report"]//span[@property="v:summary"]/text()').get()
        synopsis = synopsis and synopsis.strip()

        poster = response.xpath('//*[@id="mainpic"]/a/img/@src').get()

        film_id = response.url.split('/')[-2]

        yield MovieItem(id = film_id,
                        name = name.decode('utf8'),
                        rating = rating,
                        kind = kind,
                        duration = duration,
                        showdate = showdate,
                        language = language,
                        country = country,
                        alternate_name = alternate_name,
                        synopsis = synopsis,
                        poster = poster)

        # 演职人员
        artist_url = response.xpath('//*[@id="celebrities"]/h2/span/a/@href').getall()
        if artist_url:
            artist_url = artist_url[0]
            yield scrapy.Request('https://movie.douban.com/' + artist_url,
                                callback=self.spider_douban_movie_artist,
                                meta={'id': film_id})

        # 预告片
        tmp = response.xpath('//*[@id="related-pic"]/h2/span').get()
        m = re.findall(r'<a href="(.*trailer#trailer)">.*</a>', tmp)
        if m:
            yield scrapy.Request(m[0], callback=self.spider_douban_movie_trailer, meta={'id': film_id})

        # 剧照
        subject_id = re.findall(r'.*/(\d*)/$', response.url)
        subject_id = subject_id and subject_id[0]
        if subject_id:
            yield scrapy.Request('https://movie.douban.com/subject/%s/photos?type=S' % subject_id,
                                callback=self.spider_douban_movie_pic,
                                meta={'id': film_id})


    def spider_douban_movie_artist(self, response):
        """
        获取演职人员信息
        """
        identities = response.xpath('//*[@id="celebrities"]/div')
        for identity in identities:
            id_kind = identity.xpath('./h2/text()').get()
            id_kind = id_kind and id_kind.split(' ')[0] or ''
            artists = identity.xpath('./ul/li')
            for at in artists:
                name = at.xpath('./a/@title').get()
                avatar = at.xpath('./a/div/@style').get()
                avatar = re.findall(r'background-image: url\((.*)\)', avatar)
                role = at.xpath('./div/span[2]/@title').get()
                role = re.findall(r'\((.*)\)', role)
                role = role and role[0].split(' ') or []
                role = len(role)>1 and '饰 %s' % role[1] or ''
                yield ArtistItem(film_id=response.meta.get('id'),
                                name=name,
                                avatar=avatar and avatar[0],
                                role=role)

    def spider_douban_movie_trailer(self, response):
        """
        通过预告片列表，获取详情，并带参进入预告片播放页，返回播放页的request
        """
        identities = response.xpath('//div[@class="article"]/div[1]/ul/li')
        for identity in identities:
            video_time = identity.xpath('./a/strong/em/text()').get()
            pic = identity.xpath('./a/img/@src').get()
            name = identity.xpath('./p[1]/a/text()').get()
            next_url = identity.xpath('./p[1]/a/@href').get()
            release_date = identity.xpath('./p[@class="trail-meta"]/span/text()').get()
            meta = {
                'id': response.meta.get('id'),
                'pic': pic,
                'video_time': video_time,
                'name': name.strip(),
                'release_date': release_date,
            }
            yield scrapy.Request(next_url, callback=self.spider_douban_movie_trailer_show, meta=meta)

    def spider_douban_movie_trailer_show(self, response):
        """
        通过预告片播放页获取视频url，返回item
        """
        video = response.xpath('//video/source/@src').get()
        yield TrailerItem(film_id=response.meta.get('id'),
                            video=video,
                            pic=response.meta.get('pic'),
                            video_time=response.meta.get('video_time'),
                            name=response.meta.get('name'),
                            release_date=response.meta.get('release_date'))

    def spider_douban_movie_pic(self, response):
        """
        获取剧照
        """
        pics = response.xpath('//*[@id="content"]/div/div[1]/ul/li/div[1]/a/img/@src').getall()
        for index, item in enumerate(pics):
            yield PicItem(film_id=response.meta.get('id'), pic=item)
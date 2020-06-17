import scrapy

class MovieItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    rating = scrapy.Field()
    kind = scrapy.Field()
    duration = scrapy.Field()
    showdate = scrapy.Field()
    language = scrapy.Field()
    country = scrapy.Field()
    alternate_name = scrapy.Field()
    synopsis = scrapy.Field()
    poster = scrapy.Field()
    artist = scrapy.Field()
    trailer = scrapy.Field()
    pic = scrapy.Field()


class ArtistItem(scrapy.Item):
    film_id = scrapy.Field()
    name = scrapy.Field()
    avatar = scrapy.Field()
    role = scrapy.Field()

class TrailerItem(scrapy.Item):
    film_id = scrapy.Field()
    video = scrapy.Field()
    pic = scrapy.Field()
    video_time = scrapy.Field()
    name = scrapy.Field()
    release_date = scrapy.Field()

class PicItem(scrapy.Item):
    film_id = scrapy.Field()
    pic = scrapy.Field()

class Info1(scrapy.Item):
    id = scrapy.Field()
    country = scrapy.Field()
    page = scrapy.Field()
    name = scrapy.Field() # 影片名称
    dbname = scrapy.Field() # 豆瓣影片名称
    producter = scrapy.Field() # 出品公司
    releaser = scrapy.Field() # 发行公司
    show_time = scrapy.Field() # 公映日期
    box_office = scrapy.Field() # 总票房
    video_online = scrapy.Field() # 在线视频站

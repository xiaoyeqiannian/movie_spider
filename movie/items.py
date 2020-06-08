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


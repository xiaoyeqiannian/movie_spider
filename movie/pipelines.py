# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MoviePipeline(object):
    def process_item(self, item, spider):
        return item

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass
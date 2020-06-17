# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class MyUserAgentMiddleware(UserAgentMiddleware):
    """
    随机user agent
    """
    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.spider.name == 'info1':
            return cls(user_agent=crawler.settings.get('USER_AGENT'))
        elif crawler.spider.name == 'douban':
            return cls(user_agent=crawler.settings.get('USER_AGENT'))
        elif crawler.spider.name == 'endata':
            return cls(user_agent=crawler.settings.get('USER_AGENT'))
        elif crawler.spider.name == 'douban_explore':
            return cls(user_agent=crawler.settings.get('USER_AGENT'))

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = agent


class MovieSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MovieDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if spider.name == 'info1':
            request.cookies = {
                'uuid_n_v':'v1',
                'uuid':'508AE6E0AF7B11EA909D9FF2C00A78C337E5547100DC4DDAB455934FD2713087',
                '_csrf':'3be37af580e9381ef3c89de0bce66a3ad8589ef7aaf7bd7c3ef26823931e6192',
                '_lxsdk':'508AE6E0AF7B11EA909D9FF2C00A78C337E5547100DC4DDAB455934FD2713087',
                'Hm_lvt_703e94591e87be68cc8da0da7cbd0be2':1592275484,
                'mojo-uuid':'2f5dd10335e7f2ab210e6a7a985b483f',
                'mojo-session-id':{"id":"bf55f1e7491154feeed5890538a8abf1","time":1592281050666},
                '__mta':'247321275.1592275483847.1592281123551.1592281127159.16',
                'Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2':'592281128',
                'mojo-trace-id':16,
                '_lxsdk_s':'172bb58add1-502-e91-780%7C%7C25'
            }
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

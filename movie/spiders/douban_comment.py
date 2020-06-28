import scrapy
import re
from movie.items import CommentItem


class DoubanCommentSpider(scrapy.Spider):
    name = 'douban_comment'
    start_urls = ['https://movie.douban.com/subject/27012998/comments?start=0&limit=20&sort=new_score&status=P']

    def parse(self, response):
        print(response.url)
        comment_list = response.xpath('//div[@class="comment"]/h3')
        for item in comment_list:
            comment_vote = item.xpath('span[@class="comment-vote"]/span/text()').get()
            nickname = item.xpath('span[@class="comment-info"]/a/text()').get()
            user_url = item.xpath('span[@class="comment-info"]/a/@href').get()
            comment_time = item.xpath('span[@class="comment-info"]/span[@class="comment-time "]/text()').get()
            star = item.xpath('span[@class="comment-info"]/span[contains(@class, "rating")]/@class').get()
            print(comment_vote, nickname, user_url.split('/')[-2].strip(), comment_time.strip(), star, type(star))
            try:
                star = re.findall(r'allstar(\d+) rating', star)[0]
            except:
                print('star')
            yield CommentItem(
                    nickname = nickname,
                    userid = user_url.split('/')[-2].strip(),
                    star = star,
                    comment_time  = comment_time.strip(),
                    comment_vote = comment_vote,
            )

        if comment_list:
            r = re.findall(r'.*start=(\d+)', response.url)
            r = r and int(r[0]) or 0
            r += 20
            
            url = re.sub(r'start=\d+', 'start='+str(r), response.url, 1)
            response.meta['page'] = str(r)
            yield scrapy.Request(url,
                                callback=self.parse,
                                meta=response.meta)

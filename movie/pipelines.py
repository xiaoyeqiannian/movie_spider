# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import xlwt
import xlrd

class MoviePipeline(object):

    def __init__(self):
        self.spider_out = []

    def process_item(self, item, spider):
        for i in self.spider_out:
            if i.get('userid') == item['userid']:
                return item
        self.spider_out.append(dict(item))
        return item

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        ret = []
        if spider.name in ('douban_explore', 'info1', 'endata'):
            for v in self.spider_out:
                ret.append([
                    v.get('country'),
                    v.get('page'),
                    v.get('name'), # 影片名称
                    v.get('dbname'), # 影片名称
                    v.get('producter'), # 出品公司
                    v.get('releaser'), # 发行公司
                    v.get('show_time'), # 公映日期
                    v.get('box_office'), # 总票房
                    v.get('video_online')
                ])
            self.save2xls(spider.name, ret, ('国家', '页码', '影片名称', '豆瓣名称', '出品公司', '发行公司', '公映日期', '总票房', '在线视频站'))
        elif spider.name == 'douban_comment':
            matchs = []
            hasID = []
            try:
                __matchs = xlrd.open_workbook(r'douban_comment.xls')
                _matchs = __matchs.sheet_by_index(0)
                for index in range(_matchs.nrows-1):
                    matchs.append([_matchs.row_values(index+1)[0],
                                _matchs.row_values(index+1)[1],
                                _matchs.row_values(index+1)[2],
                                _matchs.row_values(index+1)[3],
                                _matchs.row_values(index+1)[4],
                                _matchs.row_values(index+1)[5]])
                    hasID.append(_matchs.row_values(index+1)[1])
            except:
                pass
            for v in self.spider_out:
                if v.get('userid') in hasID:
                    continue
                print(v.get('userid'), '+++')
                matchs.append([
                    v.get('nickname'),
                    v.get('userid'),
                    v.get('star'),
                    v.get('comment_time'),
                    v.get('comment_vote'),
                    v.get('comment')
                ])
            self.save2xls(spider.name, matchs, ('昵称', 'id', '评分', '评论时间', '有用', '内容'))

    def save2xls(self, name, data, xls_header):
        workbook = xlwt.Workbook(encoding = 'ascii')
        worksheet = workbook.add_sheet(name)
        for i,item in enumerate(xls_header):
            worksheet.write(0, i, item)

        for r,row in enumerate(data):
            for i,item in enumerate(row):
                worksheet.write(r+1, i, item)
        workbook.save(name+'.xls')
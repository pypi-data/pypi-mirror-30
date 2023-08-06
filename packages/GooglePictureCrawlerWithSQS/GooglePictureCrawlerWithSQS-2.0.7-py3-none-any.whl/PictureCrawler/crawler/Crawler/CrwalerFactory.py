from PictureCrawler.crawler.Crawler.CrawlerManagerGoogle import CrawlerManagerGoogle
from PictureCrawler.crawler.Crawler.CrawlerManagerBing import CrawlerManagerBing

class CrawlerFactory(object):

    def createCrawler(self, crawler_id_factory, sqsname, awscredentialprofile, awscredentialkey, awscredentialsecret, app_id):
        if crawler_id_factory == 'google':
            return CrawlerManagerGoogle(sqsname, awscredentialprofile, '', awscredentialkey,
                                                        awscredentialsecret, app_id)
        else:
            if crawler_id_factory == 'bing':
                return CrawlerManagerBing(sqsname, awscredentialprofile, '', awscredentialkey,
                                                        awscredentialsecret, app_id)
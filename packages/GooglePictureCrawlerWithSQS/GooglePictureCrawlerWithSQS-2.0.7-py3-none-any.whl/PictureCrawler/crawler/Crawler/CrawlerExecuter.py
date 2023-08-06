from PictureCrawler.crawler.Crawler.CrwalerFactory import CrawlerFactory
from PictureCrawler.crawler.Constants.CrawlerConstants import CrawlerConstants


class CrawlerExecuter(object):


    def generateOutput(self, localstorage, awssqs, crawler_id, maxAmountOfData, sqsname, awscredentialprofile, searchTerm, awscredentialkey, awscredentialsecret, app_id):

        # Execute all crawlers
        if crawler_id == 'all':
            result = {}
            for crawler_id_list in CrawlerConstants.CRAWLER_LIST:
                crawlerManager = CrawlerFactory.createCrawler(self, crawler_id_list, sqsname, awscredentialprofile,
                                                              awscredentialkey, awscredentialsecret, app_id)
                result.update(crawlerManager.startCrawl(searchTerm, localstorage, awssqs, maxAmountOfData, crawler_id_list))
            return result

        # Execute specific crawler
        else:
            if crawler_id in CrawlerConstants.CRAWLER_LIST:
                crawlerManager = CrawlerFactory.createCrawler(self, crawler_id, sqsname, awscredentialprofile, awscredentialkey, awscredentialsecret, app_id)
                return crawlerManager.startCrawl(searchTerm, localstorage, awssqs, maxAmountOfData, crawler_id)
            else:
                return {'Server_ID': app_id, 'Error': 'wrong used resource'}

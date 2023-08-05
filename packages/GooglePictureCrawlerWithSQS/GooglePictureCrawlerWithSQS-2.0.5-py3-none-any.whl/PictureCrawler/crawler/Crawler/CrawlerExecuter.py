from PictureCrawler.crawler.Crawler.CrawlerManager import CrawlerManager
import ast


class CrawlerExecuter(object):
    def generateOutput(self, localstorage, awssqs, crawler_id, maxAmountOfData, sqsname, awscredentialprofile, searchTerm):

        # Execute all crawlers
        if crawler_id == 'all':
            crawlerManager = CrawlerManager(sqsname, awscredentialprofile, '')
            return crawlerManager.startCrawl(searchTerm, ast.literal_eval(localstorage), ast.literal_eval(awssqs), maxAmountOfData)

        # Execute specific crawler
        else:
            if crawler_id == 'google':
                crawlerManager = CrawlerManager(sqsname, awscredentialprofile, '')
                return crawlerManager.startCrawl(searchTerm, ast.literal_eval(localstorage), ast.literal_eval(awssqs), maxAmountOfData)
            else:
                return {'Error': 'wrong crawler is'}

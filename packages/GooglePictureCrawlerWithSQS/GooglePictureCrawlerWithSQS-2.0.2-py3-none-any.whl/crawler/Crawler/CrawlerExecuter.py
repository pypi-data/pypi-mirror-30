from crawler.Crawler.CrawlerManager import CrawlerManager
import ast


class CrawlerExecuter(object):
    def generateOutput(self, localstorage, awssqs, crawler_id, maxAmountOfData, sqsname, awscredentialprofile, searchTerm):
        result = ''

        # Execute all crawlers
        if crawler_id == 'all':
            crawlerManager = CrawlerManager(sqsname, awscredentialprofile, '')
            crawlerManager.startCrawl(searchTerm, ast.literal_eval(localstorage), ast.literal_eval(awssqs), maxAmountOfData)
            result = crawler_id
            return {'crawler': result}

        # Execute specific crawler
        else:
            if crawler_id == 'google':
                crawlerManager = CrawlerManager(sqsname, awscredentialprofile, '')
                crawlerManager.startCrawl(searchTerm, ast.literal_eval(localstorage), ast.literal_eval(awssqs), maxAmountOfData)
                result = crawler_id
                return {'crawler': result}
            else:
                return {'crawler': 'wrong para'}

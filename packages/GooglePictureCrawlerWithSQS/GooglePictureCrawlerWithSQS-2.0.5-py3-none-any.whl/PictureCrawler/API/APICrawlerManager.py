from flask_restful import Resource, reqparse
from PictureCrawler.crawler.Crawler.CrawlerExecuter import CrawlerExecuter

class APICrawlerManager(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('localstorage', type=str)
        parser.add_argument('awssqs', type=str)
        parser.add_argument('maxAmountOfData', type=int)
        parser.add_argument('sqsname', type=str)
        parser.add_argument('awscredentialprofile', type=str)
        parser.add_argument('searchTerm', type=str)
        args = parser.parse_args()

        #Default value to execute all crawlers
        crawler_id = 'all'

        #print(localstorage, awssqs, crawler_id)
        return CrawlerExecuter.generateOutput(self, str(args['localstorage']), str(args['awssqs']),
                                              crawler_id, int(args['maxAmountOfData']),
                                              str(args['sqsname']),
                                              str(args['awscredentialprofile']),
                                              str(args['searchTerm']))


class APIConcreteCrawlerManager(Resource):
    def post(self, crawler_id):
        parser = reqparse.RequestParser()
        parser.add_argument('localstorage', type=str)
        parser.add_argument('awssqs', type=str)
        parser.add_argument('maxAmountOfData', type=int)
        parser.add_argument('sqsname', type=str)
        parser.add_argument('awscredentialprofile', type=str)
        parser.add_argument('searchTerm', type=str)
        args = parser.parse_args()

        #print(localstorage, awssqs, crawler_id)
        return CrawlerExecuter.generateOutput(self, str(args['localstorage']), str(args['awssqs']),
                                              crawler_id, int(args['maxAmountOfData']),
                                              str(args['sqsname']),
                                              str(args['awscredentialprofile']),
                                              str(args['searchTerm']))
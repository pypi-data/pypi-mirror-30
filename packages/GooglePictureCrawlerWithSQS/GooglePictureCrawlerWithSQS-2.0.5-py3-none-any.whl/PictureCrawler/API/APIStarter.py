#https://www.codementor.io/sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq

from flask import Flask
from flask_restful import Api
from PictureCrawler.API.APICrawlerManager import APICrawlerManager
from PictureCrawler.API.APICrawlerManager import APIConcreteCrawlerManager


class APIStarter(object):

     @staticmethod
     def start(myPort):
         app = Flask(__name__)
         api = Api(app)

         api.add_resource(APICrawlerManager, '/crawler')
         api.add_resource(APIConcreteCrawlerManager, '/crawler/<crawler_id>')

         #if __name__ == '__main__':
         app.run(host= '0.0.0.0',port=myPort)
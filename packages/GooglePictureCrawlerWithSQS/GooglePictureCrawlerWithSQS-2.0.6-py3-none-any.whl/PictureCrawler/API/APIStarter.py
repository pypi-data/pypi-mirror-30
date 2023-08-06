#https://www.codementor.io/sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq

from flask import Flask
from flask_restful import Api
from PictureCrawler.API.APICrawlerManager import APICrawlerManager
from PictureCrawler.API.APICrawlerManager import APIConcreteCrawlerManager

import uuid


class APIStarter(object):

     @staticmethod
     def start(myPort):
         app = Flask(__name__)
         api = Api(app)

         #Client id for load balancing
         app_id = str(uuid.uuid4())

         api.add_resource(APICrawlerManager, '/crawler', resource_class_kwargs={ 'app_id': app_id})
         api.add_resource(APIConcreteCrawlerManager, '/crawler/<crawler_id>', resource_class_kwargs={ 'app_id': app_id})

         #if __name__ == '__main__':
         app.run(host= '0.0.0.0',port=myPort)
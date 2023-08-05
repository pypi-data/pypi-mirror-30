#https://www.codementor.io/sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq

from flask import Flask, request
from flask_restful import Resource, Api
from API.APICrawlerManager import APICrawlerManager
from API.APICrawlerManager import APIConcreteCrawlerManager

def start(self):
     app = Flask(__name__)
     api = Api(app)

     api.add_resource(APICrawlerManager, '/crawler')
     api.add_resource(APIConcreteCrawlerManager, '/crawler/<crawler_id>')

     if __name__ == '__main__':
          app.run(port=5003)
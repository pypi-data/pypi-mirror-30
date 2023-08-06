from bs4 import BeautifulSoup
from urllib.request import urlopen
from PictureCrawler.crawler.Constants.CrawlerConstants import CrawlerConstants
from PictureCrawler.crawler.Constants.AWSConstants import AWSConstants
from PictureCrawler.crawler.Managers.SQSManager import SQSManager
from threading import Thread
from PictureCrawler.crawler.Crawler.Crawler import Crawler

import urllib.request
import json
import os
import uuid
import requests
import re



class CrawlerManagerBing(Crawler):

    def __init__(self, SQSQueueName, AWSCredentialsProfile, LocalStoragePath, AWScredentialkey, AWScredentialsecret,
                 app_id):
        super(CrawlerManagerBing, self).__init__(SQSQueueName, AWSCredentialsProfile, LocalStoragePath, AWScredentialkey,
                                             AWScredentialsecret, app_id)



    def _Crawler__crawlContent(self, maxAmountOfData, crawler_id):
        print("Start crawling on", CrawlerConstants.BING_URL.format(self._Crawler__userQuery))
        soup = BeautifulSoup(requests.get(CrawlerConstants.BING_URL.format(self._Crawler__userQuery)).text, 'html.parser')
        counter = 0
        crawled_data = 0

        for item in soup.find_all("div", {"class": "item"}):
            if counter == maxAmountOfData:
                break
            try:
                counter = counter + 1
                for detail in item.find_all("a"):
                    origin = detail.text
                    link = detail.attrs['href']
                    type = link.rsplit('.', 1)[-1]

                    if link == "":
                        link = 'NULL'
                    if type == "":
                        type = 'NULL'
                    if origin == "":
                        origin = 'NULL'
                    self._Crawler__actualCrawledImages.append((link, type, origin))

                    crawled_data = crawled_data + 1

                    # Create json file
                    picture_name = 'Bing_Picture_' + str(counter)
                    result_name = 'SearchResultsFor' + crawler_id
                    self._Crawler__jsonResult[result_name][picture_name] = {}
                    self._Crawler__jsonResult[result_name][picture_name]['url'] = link
                    self._Crawler__jsonResult[result_name][picture_name]['Type'] = type
                    self._Crawler__jsonResult[result_name][picture_name]['Source'] = origin
                    break
            except:
                continue

        print("Bing - Amount of crawled pictures:", crawled_data)
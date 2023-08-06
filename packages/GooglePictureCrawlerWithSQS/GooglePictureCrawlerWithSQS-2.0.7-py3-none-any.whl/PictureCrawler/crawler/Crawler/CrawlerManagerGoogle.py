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


class CrawlerManagerGoogle(Crawler):

    def __init__(self, SQSQueueName, AWSCredentialsProfile, LocalStoragePath, AWScredentialkey, AWScredentialsecret, app_id):
        super(CrawlerManagerGoogle, self).__init__(SQSQueueName, AWSCredentialsProfile, LocalStoragePath, AWScredentialkey, AWScredentialsecret, app_id)


    #Specif crawler for google (abstract method of Crawler)
    def _Crawler__crawlContent(self, maxAmountOfData, crawler_id):
        print("Start crawling on", CrawlerConstants.GOOGLE_URL.format(self._Crawler__userQuery))
        soup = self._Crawler__get_soup(CrawlerConstants.GOOGLE_URL.format(self._Crawler__userQuery), CrawlerConstants.HEADER)
        counter = 0
        crawled_data = 0

        for a in soup.find_all("div", {"class": "rg_meta"}):
            if counter == maxAmountOfData:
                break

            link, type, origin = json.loads(a.text)["ou"], json.loads(a.text)["ity"], json.loads(a.text)["isu"]
            if link == "":
                link = 'NULL'
            if type == "":
                type = 'NULL'
            if origin == "":
                origin = 'NULL'
            self._Crawler__actualCrawledImages.append((link, type, origin))

            crawled_data = crawled_data + 1
            counter = counter + 1

            #Create json file
            picture_name = 'Google_Picture_' + str(counter)
            result_name = 'SearchResultsFor' + crawler_id
            self._Crawler__jsonResult[result_name][picture_name] = {}
            self._Crawler__jsonResult[result_name][picture_name]['url'] = link
            self._Crawler__jsonResult[result_name][picture_name]['Type'] = type
            self._Crawler__jsonResult[result_name][picture_name]['Source'] = origin
        print("Google - Amount of crawled pictures:", crawled_data)
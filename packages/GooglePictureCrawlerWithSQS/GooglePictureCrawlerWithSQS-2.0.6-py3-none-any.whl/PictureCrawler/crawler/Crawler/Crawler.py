from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from urllib.request import urlopen
from PictureCrawler.crawler.Constants.CrawlerConstants import CrawlerConstants
from PictureCrawler.crawler.Constants.AWSConstants import AWSConstants
from PictureCrawler.crawler.Managers.SQSManager import SQSManager
from threading import Thread

import urllib.request
import json
import os
import uuid
import requests
import re


class Crawler(ABC):
    # private
    __userQuery1 = ""
    __app_id = ""
    __actualCrawledImages = []
    __actualCrawledImagesBing = []
    __jsonResult = {}


    def __init__(self, SQSQueueName, AWSCredentialsProfile, LocalStoragePath, AWScredentialkey, AWScredentialsecret, app_id):
        AWSConstants.AWS_QUEUE_NAME = SQSQueueName
        AWSConstants.AWS_CREDENTIAL_PROFILE = AWSCredentialsProfile
        AWSConstants.AWS_CREDENTIAL_KEY = AWScredentialkey
        AWSConstants.AWS_CREDENTIAL_SECRET = AWScredentialsecret

        self.__app_id = app_id

        if (bool(LocalStoragePath.strip())):
            CrawlerConstants.LOCAL_DIR = LocalStoragePath
        CrawlerConstants.IMAGE_FOLDER_TITLE = str(uuid.uuid4())


    # private methods
    def __get_soup(self, url, header):
        return BeautifulSoup(urlopen(urllib.request.Request(url, headers=header)), 'html.parser')

    def __saveImagesOnDisk(self):
        DIR = CrawlerConstants.LOCAL_DIR + CrawlerConstants.IMAGE_FOLDER_TITLE
        #Create folder, if necessary
        if not os.path.exists(CrawlerConstants.LOCAL_DIR):
            os.mkdir(CrawlerConstants.LOCAL_DIR)
        if not os.path.exists(DIR):
            os.mkdir(DIR)

        print("Starting disk process on path: ", DIR)
        counter = 0
        for i, (img, type, origin) in enumerate(self.__actualCrawledImages):
            try:
                req = urllib.request.Request(img, headers={'User-Agent': CrawlerConstants.HEADER})
                raw_img = urlopen(req.full_url).read()
                cntr = len([i for i in os.listdir(DIR) if CrawlerConstants.IMAGE_SUPERNAME in i]) + 1
                if len(type) == 0:
                    f = open(os.path.join(DIR, CrawlerConstants.IMAGE_SUPERNAME + "_" + str(cntr) + ".jpg"), 'wb')
                else:
                    f = open(os.path.join(DIR, CrawlerConstants.IMAGE_SUPERNAME + "_" + str(cntr) + "." + type), 'wb')

                f.write(raw_img)
                f.close()
                counter = counter + 1
            except Exception as e:
                print("Disk error; could not load: " + img)
                print(e)
        print("Finished disk process; ", counter , " images were localy stored")

    def __submitImagesToSQSQueue(self):
        sqsManager = SQSManager(AWSConstants.AWS_CREDENTIAL_PROFILE)
        sqsManager.sendMessagesToSQSQueue(self.__actualCrawledImages)


    @abstractmethod
    def __crawlContent(self, maxAmountOfData, crawler_id):
        raise NotImplementedError

    def __startCrawledDataProcess(self, safeImagesLocal, submitImagesToSQS):
        thread_safeImagesLocal = Thread(target=self.__saveImagesOnDisk)
        thread_submitImagesToSQS = Thread(target=self.__submitImagesToSQSQueue)

        if safeImagesLocal == 'True':
            thread_safeImagesLocal.start()
        if submitImagesToSQS == 'True':
            thread_submitImagesToSQS.start()

        if safeImagesLocal == 'True':
            thread_safeImagesLocal.join()
        if submitImagesToSQS == 'True':
            thread_submitImagesToSQS.join()

    # public methods
    def startCrawl(self, searchTerm, safeImagesLocal, submitImagesToSQS, maxAmountOfData, crawler_id):
        # Preperation
        self.__userQuery = searchTerm
        self.__userQuery = self.__userQuery.split()
        self.__userQuery = '+'.join(self.__userQuery)
        self.__jsonResult = {}
        self.__jsonResult['SearchTerm'] = searchTerm
        self.__jsonResult['Server_ID'] = self.__app_id
        result_name = 'SearchResultsFor' + crawler_id
        self.__jsonResult[result_name] = {}

        self._Crawler__actualCrawledImages = []
        # Crawling data from google
        self.__crawlContent(maxAmountOfData, crawler_id)

        # Process crawled data
        self.__startCrawledDataProcess(safeImagesLocal, submitImagesToSQS)

        # Provide result
        return self.__jsonResult
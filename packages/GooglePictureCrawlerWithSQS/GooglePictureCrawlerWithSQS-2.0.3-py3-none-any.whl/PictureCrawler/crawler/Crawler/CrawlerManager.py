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


class CrawlerManager(object):
    #private
    __userQuery = ""
    __actualCrawledImages = []
    __jsonResult = {}

    def __init__(self, SQSQueueName, AWSCredentialsProfile, LocalStoragePath):
        AWSConstants.AWS_QUEUE_NAME = SQSQueueName
        AWSConstants.AWS_CREDENTIAL_PROFILE = AWSCredentialsProfile
        if (bool(LocalStoragePath.strip())):
            CrawlerConstants.LOCAL_DIR = LocalStoragePath
        CrawlerConstants.IMAGE_FOLDER_TITLE = str(uuid.uuid4())

    #private methods
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
        sqsManager = SQSManager()
        sqsManager.sendMessagesToSQSQueue(self.__actualCrawledImages)

    def __crawlContent(self, maxAmountOfData):
        print("Start crawling on ", CrawlerConstants.GOOGLE_URL.format(self.__userQuery))
        soup = self.__get_soup(CrawlerConstants.GOOGLE_URL.format(self.__userQuery), CrawlerConstants.HEADER)
        self.__actualCrawledImages = []
        counter = 0

        for a in soup.find_all("div", {"class": "rg_meta"}):
            if counter == maxAmountOfData:
                break

            #print(json.loads(a.text))
            link, type, origin = json.loads(a.text)["ou"], json.loads(a.text)["ity"], json.loads(a.text)["isu"]
            if link == "":
                link = 'NULL'
            if type == "":
                type = 'jpg'
            if origin == "":
                origin = 'NULL'
            self.__actualCrawledImages.append((link, type, origin))

            counter = counter + 1

            #Create json file
            picture_name = 'Picture_' + str(counter)
            self.__jsonResult['SearchResults'][picture_name] = {}
            self.__jsonResult['SearchResults'][picture_name]['url'] = link
            self.__jsonResult['SearchResults'][picture_name]['Type'] = type
            self.__jsonResult['SearchResults'][picture_name]['Source'] = origin

        print("Amount of crawled pictures:", len(self.__actualCrawledImages))

    def __startCrawledDataProcess(self, safeImagesLocal, submitImagesToSQS):
        thread_safeImagesLocal = Thread(target=self.__saveImagesOnDisk)
        thread_submitImagesToSQS = Thread(target=self.__submitImagesToSQSQueue)

        if safeImagesLocal == True:
            thread_safeImagesLocal.start()
        if submitImagesToSQS == True:
            thread_submitImagesToSQS.start()

        if safeImagesLocal == True:
            thread_safeImagesLocal.join()
        if submitImagesToSQS == True:
            thread_submitImagesToSQS.join()


    #public methods
    def startCrawl(self, searchTerm, safeImagesLocal, submitImagesToSQS, maxAmountOfData):
        #Preperation
        self.__userQuery = searchTerm
        self.__userQuery = self.__userQuery.split()
        self.__userQuery = '+'.join(self.__userQuery)
        self.__jsonResult = {}
        self.__jsonResult['SearchTerm'] = searchTerm
        self.__jsonResult['SearchResults'] = {}

        #Crawling data from google
        self.__crawlContent(maxAmountOfData)

        #Process crawled data
        self.__startCrawledDataProcess(safeImagesLocal, submitImagesToSQS)

        #Provide result
        return self.__jsonResult
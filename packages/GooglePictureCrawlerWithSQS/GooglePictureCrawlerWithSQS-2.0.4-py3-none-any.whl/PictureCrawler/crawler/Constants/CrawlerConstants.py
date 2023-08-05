import os


class CrawlerConstants(object):
    #Save images on disk
    LOCAL_DIR = os.path.join(os.path.join(os.path.expanduser('~')), 'PictureCrawler/')
    IMAGE_FOLDER_TITLE = ''
    IMAGE_SUPERNAME = "picture"

    #Query attributes
    GOOGLE_URL = "https://www.google.co.in/search?q={}&source=lnms&tbm=isch"
    HEADER = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }

    #AWS attributes
https://pypi.org/manage/project/GooglePictureCrawlerWithSQS/releases/

**Data Crawler for Google Pictures**

This crawler is suitable to crawl data from google pictures based on a given combination of search terms. The result will be stored on disk and/or in a sqs queue within AWS.

- max amount of data to fetch: 100

**Requirements:**
- AWS credentials
- SQS queue name

**Example Call**
from API.APIStarter import APIStarter
APIStarter.start(5002)

**Routs**
- /crawler (POST)
    -- Flag: localstorage
    -- Flag: awssqs name
- /crawler/<crawler_id> (POST)
    -- Flag: localstorage
    -- Flag: awssqs name


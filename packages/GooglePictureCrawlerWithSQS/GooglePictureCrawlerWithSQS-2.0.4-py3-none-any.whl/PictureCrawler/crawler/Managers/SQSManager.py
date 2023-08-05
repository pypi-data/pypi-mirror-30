import boto3
import uuid

from PictureCrawler.crawler.Constants.AWSConstants import AWSConstants


class SQSManager(object):
    __sqsQueue = ''

    def __init__(self):
        session = boto3.Session(profile_name=AWSConstants.AWS_CREDENTIAL_PROFILE)
        sqsClient = session.resource('sqs')
        self.__sqsQueue = sqsClient.get_queue_by_name(QueueName=AWSConstants.AWS_QUEUE_NAME)

    def sendMessagesToSQSQueue(self, crawledImages):
        print('Starting queue process on' , self.__sqsQueue.url , 'for', len(crawledImages) , 'images.')

        # Send message to SQS queue based on crawledImages
        for i, (img, type, origin) in enumerate(crawledImages):
            self.__sqsQueue.send_message(
                QueueUrl=self.__sqsQueue.url,
                MessageAttributes={
                    'Img': {
                        'DataType': 'String',
                        'StringValue': img
                    },
                    'Type': {
                        'DataType': 'String',
                        'StringValue': type
                    },
                    'Origin': {
                        'DataType': 'String',
                        'StringValue': origin
                    }
                },
                MessageBody=(
                    img
                ),
                MessageDeduplicationId=origin,
                MessageGroupId = 'general'
            )
        print('All messages sent to sqs queue:', AWSConstants.AWS_QUEUE_NAME)
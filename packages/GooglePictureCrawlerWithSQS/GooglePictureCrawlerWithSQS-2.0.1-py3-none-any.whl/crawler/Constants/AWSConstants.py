class AWSConstants(object):
    # Any clients created from this session will use credentials
    # from the [sqs] section of ~/.aws/credentials.
    AWS_CREDENTIAL_PROFILE = 'sqs'

    AWS_QUEUE_NAME = 'PictureHolderQueue.fifo'
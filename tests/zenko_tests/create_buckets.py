#!/usr/bin/env python
from boto3 import Session
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError
from azure.storage.queue import QueueServiceClient
import os
import logging

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger('create_buckets')

def get_env(key, default=None, error=False):
    if not error:
        return os.environ.get(key, default)
    return os.environ[key]

def bucket_safe_create(bucket):
    try:
        _log.info('Creating bucket %s' % bucket.name)
        bucket.create()
    except bucket.meta.client.exceptions.BucketAlreadyOwnedByYou:
        _log.info('Bucket %s already exists!' % bucket.name)
    except Exception as exp:  # pylint: disable=broad-except
        _log.info('Error creating bucket %s - %s' % (bucket.name, str(exp)))
        raise exp

def create_ring_buckets():
    VERIFY_CERTIFICATES = get_env('VERIFY_CERTIFICATES', False)
    RING_S3C_ACCESS_KEY = get_env('RING_S3C_ACCESS_KEY')
    RING_S3C_SECRET_KEY = get_env('RING_S3C_SECRET_KEY')
    RING_S3C_INGESTION_SRC_BUCKET_NAME = get_env('RING_S3C_INGESTION_SRC_BUCKET_NAME')
    RING_S3C_ENDPOINT = get_env('RING_S3C_ENDPOINT')
    ENABLE_RING_TESTS = get_env('ENABLE_RING_TESTS')

    # Disable if Ring is not enabled
    if ENABLE_RING_TESTS == "false":
        return

    s3c = Session(aws_access_key_id=RING_S3C_ACCESS_KEY,
            aws_secret_access_key=RING_S3C_SECRET_KEY)
    ring_s3c_client = s3c.resource('s3', endpoint_url=RING_S3C_ENDPOINT,
                      verify=VERIFY_CERTIFICATES)

    ## Creating S3C buckets
    _log.info('Creating S3C buckets...')
    bucket_safe_create(ring_s3c_client.Bucket(RING_S3C_INGESTION_SRC_BUCKET_NAME))
    ring_s3c_client.Bucket(RING_S3C_INGESTION_SRC_BUCKET_NAME).Versioning().enable()

def create_aws_buckets():
    VERIFY_CERTIFICATES = get_env('VERIFY_CERTIFICATES', False)
    AWS_ACCESS_KEY = get_env('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = get_env('AWS_SECRET_KEY')
    AWS_FAIL_BUCKET_NAME = get_env('AWS_FAIL_BUCKET_NAME')
    AWS_ENDPOINT = get_env('AWS_ENDPOINT')

    s3c = Session(aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY)
    aws_s3c_client = s3c.resource('s3', endpoint_url=AWS_ENDPOINT,
            verify=VERIFY_CERTIFICATES)

    ## Creating AWS buckets
    _log.info('Creating AWS buckets...')
    bucket_safe_create(aws_s3c_client.Bucket(AWS_FAIL_BUCKET_NAME))
    aws_s3c_client.Bucket(AWS_FAIL_BUCKET_NAME).Versioning().enable()

def create_azure_containers():
    AZURE_BACKEND_ENDPOINT = get_env("AZURE_BACKEND_ENDPOINT")
    AZURE_ACCOUNT_NAME = get_env("AZURE_ACCOUNT_NAME")
    AZURE_SECRET_KEY = get_env("AZURE_SECRET_KEY")
    AZURE_CRR_BUCKET_NAME = get_env("AZURE_CRR_BUCKET_NAME")
    AZURE_ARCHIVE_BUCKET_NAME = get_env("AZURE_ARCHIVE_BUCKET_NAME")
    AZURE_ARCHIVE_BUCKET_NAME_2 = get_env("AZURE_ARCHIVE_BUCKET_NAME_2")

    credential = AzureNamedKeyCredential(name=AZURE_ACCOUNT_NAME,
            key=AZURE_SECRET_KEY)
    blob_service_client = BlobServiceClient(account_url=AZURE_BACKEND_ENDPOINT,
            credential=credential)
    
    ## Creating Azure buckets
    _log.info('Creating Azure buckets...')
    for bucket_name in [AZURE_CRR_BUCKET_NAME, AZURE_ARCHIVE_BUCKET_NAME, AZURE_ARCHIVE_BUCKET_NAME_2]:
        try:
            _log.info('Creating bucket %s' % bucket_name)
            blob_service_client.create_container(name=bucket_name)
        except ResourceExistsError:
            _log.info('Container %s already exists!' % bucket_name)


def create_azure_queues():
    AZURE_BACKEND_QUEUE_ENDPOINT = get_env("AZURE_BACKEND_QUEUE_ENDPOINT")
    AZURE_ACCOUNT_NAME = get_env("AZURE_ACCOUNT_NAME")
    AZURE_SECRET_KEY = get_env("AZURE_SECRET_KEY")
    AZURE_ARCHIVE_QUEUE_NAME = get_env("AZURE_ARCHIVE_QUEUE_NAME")

    credential = AzureNamedKeyCredential(name=AZURE_ACCOUNT_NAME,
            key=AZURE_SECRET_KEY)

    queue_client = QueueServiceClient(account_url=AZURE_BACKEND_QUEUE_ENDPOINT,
            credential=credential)

    ## Creating Azure queue
    _log.info('Creating Azure queues...')
    try:
        _log.info('Creating queue %s' % AZURE_ARCHIVE_QUEUE_NAME)
        queue_client.create_queue(name=AZURE_ARCHIVE_QUEUE_NAME)
    except ResourceExistsError:
        _log.info('Queue %s already exists!' % AZURE_ARCHIVE_QUEUE_NAME)

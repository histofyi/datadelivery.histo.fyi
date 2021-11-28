import boto3
import json
import logging

class s3Provider():

    client = None

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region):
        self.client = boto3.client('s3',
        aws_access_key_id = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key,
        region_name = aws_region
    )


    def get(self, bucket, key):
        data = self.client.get_object(Bucket=bucket, Key=key)['Body'].read()
        if data:
            return data, True, None
        else:
            return None, False, {
                'key': key,
                'message': 'not_found'
            }



import hmac
import base64
import hashlib
import boto3

from awstools._aws import AwsManager


class S3Manager(AwsManager):
    RESOURCE_NAME = 's3'
    CLIENT_NAME = 's3'

    def get_folder(self, bucket, prefix):
        bucket = self.resource.Bucket(bucket)
        return bucket.objects.filter(Prefix=prefix.lstrip('/'))

    def download_folder(self, bucket, prefix):
        for object in self.get_folder(bucket, prefix):
            yield object.get()

    def get_file(self, bucket, file):
        return self.resource.Object(bucket, file.lstrip('/'))

    def download_file(self, bucket, file):
        return self.get_file(bucket, file).get()

    def upload_stream(self, bucket, key, body, **kwargs):
        return self.client.put_object(Bucket=bucket,
                                      Key=key,
                                      Body=body,
                                      **kwargs)

    def sign_policy(self, policy):
        """ Sign and return the policy document for a simple upload.
        http://aws.amazon.com/articles/1434/#signyours3postform """
        signed_policy = base64.b64encode(policy)
        sig = hmac.new(self.secret_key,
                       signed_policy,
                       hashlib.sha1)
        return {'policy': signed_policy,
                'signature': base64.b64encode(sig.digest())}

    def sign_headers(self, headers):
        """ Sign and return the headers for a chunked upload. """
        sig = hmac.new(self.secret_key,
                       headers.encode(),
                       hashlib.sha1)
        return {'signature': base64.b64encode(sig.digest())}

    def copy_file(self, src_bucket, src_key, bucket, key):
        new_file = self.resource.Object(bucket, key)
        return new_file.copy_from(CopySource='%s/%s' % (src_bucket, src_key))

    def rename_file(self, src_bucket, src_key, new_key):
        new_file = self.copy_file(src_bucket, src_key, src_bucket, new_key)
        self.delete_file(src_bucket, src_key)
        return new_file

    def delete_file(self, bucket, key):
        aws_key = self.resource.Object(bucket, key)
        aws_key.delete()
        return ''

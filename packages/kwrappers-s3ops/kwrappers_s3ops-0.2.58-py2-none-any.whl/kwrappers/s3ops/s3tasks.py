import sys
from .s3 import S3
from botocore.exceptions import ClientError

from kwrappers.util.logger import get_log
LOG = get_log()


# Python 2/3 compatability
if sys.version_info.major >= 3:
    STRING_TYPE = str
else:  # if linting in python 3 the next line will give undefined error
    STRING_TYPE = basestring  # noqa: F821


class S3Tasks:

    def __init__(self, session):
        self.s3 = S3(session)

    def checkForFile(self, bucket, key):
        try:
            response = self.s3.checkForFile(
                Bucket=bucket,
                Delimiter=key,
            )
            if len(response.Contents) > 0:
                print("found")
            else:
                print("not found")
        except ClientError as err:
            LOG.warn(err)
            sys.exit(1)

    def checkForFileV2(self, bucket, filename):
        try:
            response = self.s3.list_objects_v2(
                Bucket=bucket,
                Prefix=filename
            )
            if len(response.Contents) > 0:
                return True
            else:
                return False
        except ClientError as err:
            LOG.warn(err)
            sys.exit(1)

    def uploadFile(self, filename, bucket, key):
        try:
            self.s3.uploadFile(filename=filename, bucket=bucket, key=key)
        except ClientError as err:
            LOG.warn(err)
            sys.exit(1)

    def bucket_exists(self, bucket_name):
        return bucket_name in [bucket['Name'] for bucket in self.s3.list_buckets()['Buckets']]

    def get_bucket(self, bucket_name, region, create=False):
        """Returns Bucket object.  Create the bucket if it doesn't exist using create=True"""

        # ClientError if problem with the bucket name, If this is slow consdider only checking AFTER failure
        if create and not self.bucket_exists(bucket_name):
            self.s3.create_bucket(bucket_name, region)
        return self.s3.resource.Bucket(bucket_name)


def upload_object(bucket, dest_filename, binary_contents, kms_key=None, session=None):
    """ if bucket is string type, a session must be provided.  """

    specs = {
        'Key': dest_filename,
        'Body': binary_contents,
    }

    if kms_key:
        specs['ServerSideEncryption'] = 'aws:kms'
        specs['SSEKMSKeyId'] = kms_key

    if isinstance(bucket, STRING_TYPE):
        if not session:
            msg = "A session must be provided with bucket as a string.  Alternatively use S3Tasks.get_bucket"
            LOG.error(msg)
            raise Exception(msg)

        s3t = S3Tasks(session)
        bucket = s3t.get_bucket(bucket, session.region_name)

    try:
        res = bucket.put_object(**specs)
    except ClientError as ex:
        LOG.error("Bucket '{}' may not exist.  Consider using 'sanitise_bucket_name' and 'get_bucket'".format(bucket.name))
        raise ex

    return res


def sanitise_bucket_name(seed):
    """Sanitize the seed according to the s3 rules [here]
        (http://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html)
        """

    # if 3 > len(seed)
    # if len(seed) > 63
    # if consecutive periods
    # if dashes adjacent to periods
    # if ends with dash

    return seed.lower().replace('_', '-')

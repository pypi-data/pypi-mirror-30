# -*- coding: utf-8 -*-

"""Main module."""

import s3io
import joblib


class JoblibS3(object):
    def __init__(self, aws_key, aws_private_key, bucket=None, compression_type="gzip", compression_rate=3):
        self.aws_key = aws_key
        self.aws_private_key = aws_private_key
        self.compression_type = compression_type
        self.compression_rate = compression_rate
        self.compress = (self.compression_type, self.compression_rate) \
            if self.compression_type and self.compression_rate else None
        self.bucket = bucket

        self.credentials = dict(
            aws_access_key_id=self.aws_key,
            aws_secret_access_key=self.aws_private_key,
        )

    def save(self, obj, filename, bucket=None):
        # Dump in an S3 file is easy with Joblib
        bucket_to_save = bucket if bucket else self.bucket
        if bucket_to_save is None:
            raise AttributeError("Bucket must be specified")
        with s3io.open('s3://{0}/{1}'.format(bucket, filename), mode='w',
                       **self.credentials) as s3_file:
            joblib.dump(obj, s3_file, compress=self.compress)

    def load(self, filename, bucket=None):
        bucket_to_save = bucket if bucket else self.bucket
        if bucket_to_save is None:
            raise AttributeError("Bucket must be specified")

        with s3io.open('s3://{0}/{1}'.format(bucket if bucket else self.bucket, filename), mode='r',
                       **self.credentials) as s3_file:
            obj = joblib.load(s3_file)

        return obj


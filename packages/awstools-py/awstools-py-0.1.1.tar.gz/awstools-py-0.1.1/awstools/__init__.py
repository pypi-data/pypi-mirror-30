"""
  ====================
  `AWS Tools`
  ====================
  Simple wrappers for boto3 that assist with typical Amazon Web Services
  transactions.

  2015 Jared Lunde (c) The MIT License (MIT)
  http://github.com/jaredlunde

"""
from awstools._aws import *
from awstools.ec2 import *
from awstools.encryption import *
from awstools.events import *
from awstools.s3 import *
from awstools.transcoder import *
from awstools.watermark import *

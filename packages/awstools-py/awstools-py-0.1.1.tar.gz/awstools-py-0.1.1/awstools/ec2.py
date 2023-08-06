from awstools._aws import *


__all__ = ('InstanceManager',)


'''
instance = ec2.create_instances(
    DryRun=True|False,
    ImageId='string',
    MinCount=123,
    MaxCount=123,
    KeyName='string',
    SecurityGroups=[
        'string',
    ],
    SecurityGroupIds=[
        'string',
    ],
    UserData='string',
    InstanceType='t1.micro'|'m1.small'|'m1.medium'|'m1.large'|'m1.xlarge'|'m3.medium'|'m3.large'|'m3.xlarge'|'m3.2xlarge'|'m4.large'|'m4.xlarge'|'m4.2xlarge'|'m4.4xlarge'|'m4.10xlarge'|'t2.nano'|'t2.micro'|'t2.small'|'t2.medium'|'t2.large'|'m2.xlarge'|'m2.2xlarge'|'m2.4xlarge'|'cr1.8xlarge'|'x1.4xlarge'|'x1.8xlarge'|'x1.16xlarge'|'x1.32xlarge'|'i2.xlarge'|'i2.2xlarge'|'i2.4xlarge'|'i2.8xlarge'|'hi1.4xlarge'|'hs1.8xlarge'|'c1.medium'|'c1.xlarge'|'c3.large'|'c3.xlarge'|'c3.2xlarge'|'c3.4xlarge'|'c3.8xlarge'|'c4.large'|'c4.xlarge'|'c4.2xlarge'|'c4.4xlarge'|'c4.8xlarge'|'cc1.4xlarge'|'cc2.8xlarge'|'g2.2xlarge'|'g2.8xlarge'|'cg1.4xlarge'|'r3.large'|'r3.xlarge'|'r3.2xlarge'|'r3.4xlarge'|'r3.8xlarge'|'d2.xlarge'|'d2.2xlarge'|'d2.4xlarge'|'d2.8xlarge',
    Placement={
        'AvailabilityZone': 'string',
        'GroupName': 'string',
        'Tenancy': 'default'|'dedicated'|'host',
        'HostId': 'string',
        'Affinity': 'string'
    },
    KernelId='string',
    RamdiskId='string',
    BlockDeviceMappings=[
        {
            'VirtualName': 'string',
            'DeviceName': 'string',
            'Ebs': {
                'SnapshotId': 'string',
                'VolumeSize': 123,
                'DeleteOnTermination': True|False,
                'VolumeType': 'standard'|'io1'|'gp2'|'sc1'|'st1',
                'Iops': 123,
                'Encrypted': True|False
            },
            'NoDevice': 'string'
        },
    ],
    Monitoring={
        'Enabled': True|False
    },
    SubnetId='string',
    DisableApiTermination=True|False,
    InstanceInitiatedShutdownBehavior='stop'|'terminate',
    PrivateIpAddress='string',
    ClientToken='string',
    AdditionalInfo='string',
    NetworkInterfaces=[
        {
            'NetworkInterfaceId': 'string',
            'DeviceIndex': 123,
            'SubnetId': 'string',
            'Description': 'string',
            'PrivateIpAddress': 'string',
            'Groups': [
                'string',
            ],
            'DeleteOnTermination': True|False,
            'PrivateIpAddresses': [
                {
                    'PrivateIpAddress': 'string',
                    'Primary': True|False
                },
            ],
            'SecondaryPrivateIpAddressCount': 123,
            'AssociatePublicIpAddress': True|False
        },
    ],
    IamInstanceProfile={
        'Arn': 'string',
        'Name': 'string'
    },
    EbsOptimized=True|False
)
'''
class InstanceManager(AwsManager):

    def create(self):
        pass

    def duplicate(self):
        pass

    def terminate(self):
        pass

    def stop(self):
        pass

    def get(self):
        pass

import os.path

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3_assets as S3asset
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkLabWebServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        # Create a VPC. CDK by default creates and attaches internet gateway for VPC
        cdk_lab_vpc = ec2.Vpc(self, "cdk_lab_vpc", 
                            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
                            subnet_configuration=[ec2.SubnetConfiguration(name="PublicSubnet01",subnet_type=ec2.SubnetType.PUBLIC)]
                            )
        

        # Instance Role and SSM Managed Policy
        InstanceRole = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        InstanceRole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        # Create an EC2 instance
        cdk_lab_web_instance = ec2.Instance(self, "cdk_lab_web_instance", vpc=cdk_lab_vpc,
                                            instance_type=ec2.InstanceType("t2.micro"),
                                            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
                                            role=InstanceRole)


        # Script in S3 as Asset
        dirname = os.path.dirname(__file__)
        webinitscriptasset = S3asset(self, "Asset", path=os.path.join(dirname, "configure.sh"))
        asset_path = cdk_lab_web_instance.user_data.add_s3_download_command(
            bucket=webinitscriptasset.bucket,
            bucket_key=webinitscriptasset.s3_object_key
        )

        # Userdata executes script from S3
        cdk_lab_web_instance.user_data.add_execute_file_command(
            file_path=asset_path
            )
        webinitscriptasset.grant_read(cdk_lab_web_instance.role)
        
        # Allow inbound HTTP traffic in security groups
        cdk_lab_web_instance.connections.allow_from_any_ipv4(ec2.Port.tcp(80))

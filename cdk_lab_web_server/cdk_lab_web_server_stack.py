import os.path

from aws_cdk.aws_s3_assets import Asset as S3asset

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
    # aws_sqs as sqs,
)

from constructs import Construct

dirname = os.path.dirname(__file__)
        
class CdkLabWebServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cdk_lab_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Instance Role and SSM Managed Policy
        InstanceRole = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        InstanceRole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        # Create an EC2 instance
        cdk_lab_web_instance1 = ec2.Instance(self, "cdk_lab_web_instance1", vpc=cdk_lab_vpc,
                                            instance_type=ec2.InstanceType("t2.micro"),
                                            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
                                            role=InstanceRole)

        # Create an EC2 instance
        cdk_lab_web_instance2 = ec2.Instance(self, "cdk_lab_web_instance2", vpc=cdk_lab_vpc,
                                            instance_type=ec2.InstanceType("t2.micro"),
                                            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
                                            role=InstanceRole)

        

        # Script in S3 as Asset1
        webinitscriptasset1 = S3asset(self, "Asset1", path=os.path.join(dirname, "configure.sh"))
        asset_path1 = cdk_lab_web_instance1.user_data.add_s3_download_command(
            bucket=webinitscriptasset1.bucket,
            bucket_key=webinitscriptasset1.s3_object_key
        )

        # Userdata executes script from S3
        cdk_lab_web_instance1.user_data.add_execute_file_command(
            file_path=asset_path1
            )
        webinitscriptasset1.grant_read(cdk_lab_web_instance1.role)
        

        # Script in S3 as Asset2
        webinitscriptasset2 = S3asset(self, "Asset2", path=os.path.join(dirname, "configure.sh"))
        asset_path2 = cdk_lab_web_instance2.user_data.add_s3_download_command(
            bucket=webinitscriptasset2.bucket,
            bucket_key=webinitscriptasset2.s3_object_key
        )

        # Userdata executes script from S3
        cdk_lab_web_instance2.user_data.add_execute_file_command(
            file_path=asset_path2
            )
        webinitscriptasset2.grant_read(cdk_lab_web_instance2.role)


        # Allow inbound HTTP traffic in security groups
        cdk_lab_web_instance1.connections.allow_from_any_ipv4(ec2.Port.tcp(80))

        # Allow inbound HTTP traffic in security groups
        cdk_lab_web_instance2.connections.allow_from_any_ipv4(ec2.Port.tcp(80))        

from os import environ
from huggingface_sagemaker.utils import (
    LATEST_PYTORCH_VERSION,
    LATEST_TRANSFORMERS_VERSION,
    region_dict,
)
from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core, aws_sagemaker as sagemaker, aws_iam as iam


# policies based on https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html#sagemaker-roles-createmodel-perms
iam_sagemaker_actions = [
    "sagemaker:*",
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "ecr:BatchCheckLayerAvailability",
    "ecr:GetAuthorizationToken",
    "cloudwatch:PutMetricData",
    "cloudwatch:GetMetricData",
    "cloudwatch:GetMetricStatistics",
    "cloudwatch:ListMetrics",
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:DescribeLogStreams",
    "logs:PutLogEvents",
    "logs:GetLogEvents",
    "s3:CreateBucket",
    "s3:ListBucket",
    "s3:GetBucketLocation",
    "s3:GetObject",
    "s3:PutObject",
]


def get_image_uri(
    region=None, transformmers_version=LATEST_TRANSFORMERS_VERSION, pytorch_version=LATEST_PYTORCH_VERSION
):
    # return f"{region_dict[region]}.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-inference:{pytorch_version}-transformers{transformmers_version}-cpu-py36-ubuntu18.04"
    return "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.8.1-transformers4.10.2-gpu-py36-cu111-ubuntu18.04"


class HuggingfaceSagemaker(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Create SageMaker model
        execution_role = kwargs.pop("role", None)
        # hf_model = kwargs.pop("model", "")
        huggingface_model = core.CfnParameter(
            self,
            "model",
            type="String",
            default="",
        ).value_as_string
        huggingface_task = core.CfnParameter(
            self,
            "task",
            type="String",
            default=None,
        ).value_as_string
        # model_data = kwargs.pop("modelData",None)

        image_uri = get_image_uri(region=self.region)

        if execution_role is None:
            execution_role = iam.Role(
                self, "hf_sagemaker_execution_role", assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com")
            )
            execution_role.add_to_policy(iam.PolicyStatement(resources=["*"], actions=iam_sagemaker_actions))

        container_environment = {"HF_MODEL_ID": huggingface_model, "HF_TASK": huggingface_task}
        container = sagemaker.CfnModel.ContainerDefinitionProperty(environment=container_environment, image=image_uri)

        model = sagemaker.CfnModel(
            self,
            "hf_model",
            execution_role_arn=execution_role.role_arn,
            primary_container=container,
            model_name=f'model-{huggingface_model.replace("_","-").replace("/","--")}',
        )

        endpoint_configuration = sagemaker.CfnEndpointConfig(
            self,
            "hf_endpoint_config",
            endpoint_config_name=f'config-{huggingface_model.replace("_","-").replace("/","--")}',
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    initial_instance_count=1,
                    instance_type="ml.m5.xlarge",
                    model_name=model.model_name,
                    initial_variant_weight=1.0,
                    variant_name=model.model_name,
                )
            ],
        )
        endpoint = sagemaker.CfnEndpoint(
            self,
            "hf_endpoint",
            endpoint_name=f'endpoint-{huggingface_model.replace("_","-").replace("/","--")}',
            endpoint_config_name=endpoint_configuration.endpoint_config_name,
        )
        endpoint_configuration.node.add_dependency(model)
        endpoint.node.add_dependency(endpoint_configuration)

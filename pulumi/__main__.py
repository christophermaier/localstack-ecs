from typing import Optional, Mapping, Union
import pulumi
import pulumi_aws as aws
import json

def _environment_from_map(env):
    """
    Generate a list of environment variable dictionaries for an ECS task container definition from a standard dictionary.
    """
    return [{"name": k, "value": v } for (k,v) in env.items()]


name = "testing"

cluster = aws.ecs.Cluster(f"{name}-cluster")

task_role = aws.iam.Role(
    f"{name}-task-role",
    description=f"Fargate task role for {name}",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                }
            ],
        }
    ),
)

execution_role = aws.iam.Role(
    f"{name}-execution-role",
    description=f"Fargate execution role for {name}",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                }
            ],
        }
    ),
)

log_group = aws.cloudwatch.LogGroup(
    f"{name}-log-group",
    name=f"/localstack-ecs/{name}",
)

task = aws.ecs.TaskDefinition(
    f"{name}-task",
    family=f"{name}-family",
    container_definitions=pulumi.Output.all(log_group.name).apply(
        lambda inputs: json.dumps(
            [
                {
                    "name": "TestContainer",
                    "command": ["/test"],
                    "image": "localstack-ecs-test",
                    "environment": [
                        {"name": "FOO",
                         "value": "BAR"},
                        {"name": "MESSAGE",
                         "value": "HELLO WORLD"}
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-stream-prefix": "logs",
                            "awslogs-region": aws.get_region().name,
                            "awslogs-group": inputs[0] # log_group name
                        }
                    }
                },
            ]
        )
    ),
    requires_compatibilities=[ "FARGATE" ],
    cpu=256,
    memory=512,
    network_mode="awsvpc", # only option for Fargate
    task_role_arn=task_role.arn,
    execution_role_arn=execution_role.arn,
)

vpc = aws.ec2.Vpc(
    f"{name}-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
)

subnet = aws.ec2.Subnet(
    f"{name}-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.0.0/18",
)

security_group = aws.ec2.SecurityGroup(
    f"{name}-security-group",
    vpc_id=vpc.id,
)

service = aws.ecs.Service(
    f"{name}-service",
    cluster=cluster.arn,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        assign_public_ip=False,
        subnets=[subnet.id],
        security_groups=[security_group.id]
    ),
    launch_type="FARGATE",
    desired_count=1,
    deployment_minimum_healthy_percent=50,
    task_definition=task.arn,
)

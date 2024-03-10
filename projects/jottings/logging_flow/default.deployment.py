from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import logging_flow

az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("logging-test")

logging_flow_deployment = Deployment.build_from_flow(
    flow=logging_flow,
    name="Default",
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path="logging_test__default/",
)


logging_flow_deployment.apply(upload=True)
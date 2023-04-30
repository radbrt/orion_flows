from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.server.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import storage_write

az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("base")

storage_write_deployment = Deployment.build_from_flow(
    flow=storage_write,
    name="Default Deployment",
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path="some_flow/",
)


storage_write_deployment.apply()
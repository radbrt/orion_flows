from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.server.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import coiled

deployment_name = "Default"

flow_name = coiled.name
storage_path = deployment_name.lower().replace(" ", "_") + flow_name.lower().replace(" ", "_") + '/'


az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("base")

coiled_deployment = Deployment.build_from_flow(
    flow=coiled,
    name=deployment_name,
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path=storage_path,
)


coiled_deployment.apply()
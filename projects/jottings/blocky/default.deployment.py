from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import blocky

az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("simple")

blocky_deployment = Deployment.build_from_flow(
    flow=blocky,
    name="Default Deployment",
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    infra_overrides={"image": "radbrt/prefect_azure:latest", "namespace": "prefect2"},
    work_queue_name="kubernetes",
    path=os.getcwd()[os.getcwd().find("orion_flows"):],
)


blocky_deployment.apply()
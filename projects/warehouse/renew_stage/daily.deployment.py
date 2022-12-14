from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import main

az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("simple")

daily_deployment = Deployment.build_from_flow(
    flow=main,
    name="Daily key rotation",
    version="1",
    tags=["scheduled", "daily"],
    schedule=CronSchedule(cron="0 0 * * *"),
    storage=az_block,
    infrastructure=kubernetes_job_block,
    infra_overrides={"image": "radbrt/prefect_azure:latest", "namespace": "prefect2"},
    work_queue_name="kubernetes",
    path=os.getcwd()[os.getcwd().find("orion_flows"):],
)


daily_deployment.apply()


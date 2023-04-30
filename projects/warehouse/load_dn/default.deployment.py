from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.server.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import load_dn

deployment_name = "Default Deployment"

flow_name = load_dn.name
storage_path = deployment_name.lower().replace(" ", "_") + flow_name.lower().replace(" ", "_") + '/'


az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("load-rss")

load_dn_deployment = Deployment.build_from_flow(
    flow=load_dn,
    name=deployment_name,
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    schedule=CronSchedule(cron="0 * * * *", timezone="Europe/Oslo"),
    work_queue_name="kubernetes",
    path=storage_path,
)


load_dn_deployment.apply()
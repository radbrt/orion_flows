from prefect.deployments import Deployment
from flow import main_hello_flow
from prefect.filesystems import Azure
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os
import uuid
from prefect_azure.container_instance import AzureContainerInstanceJob

azure_container_instance_job_block = AzureContainerInstanceJob.load("aci")
# Import flow function from flow.py
from flow import main_hello_flow

az_block = Azure.load("twentysix")
# kubernetes_job_block = KubernetesJob.load("orion-mini")

daily_deployment = Deployment.build_from_flow(
    flow=main_hello_flow,
    name="Daily Hello Flow",
    version="1",
    tags=["scheduled", "daily"],
    schedule=CronSchedule(cron="0 0 * * *", timezone="America/Chicago"),
    storage=az_block,
    infrastructure=azure_container_instance_job_block,
    work_queue_name="armaci",
    path=str(uuid.uuid4()),
)


daily_deployment.apply(upload=True)
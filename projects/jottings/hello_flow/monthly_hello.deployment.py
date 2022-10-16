from prefect.deployments import Deployment
from flow import main_hello_flow
from prefect.filesystems import Azure
from prefect.infrastructure import KubernetesJob
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

az_block = Azure.load("twentysix")

monthly_deployment = Deployment.build_from_flow(
    flow=main_hello_flow,
    flow_name="Monthly Hello Flow",
    name="Monthly Hello Flow",
    version="1",
    tags=["scheduled", "daily"],
    schedule=CronSchedule(cron="1 2 1 * *", timezone="America/Chicago"),
    storage=az_block,
    infra_overrides={"image": "radbrt/prefect_azure:latest", "namespace": "prefect2"},
    work_queue_name="kubernetes",
    path=os.getcwd()[os.getcwd().find("orion_flows"):],
)


monthly_deployment.apply()
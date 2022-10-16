from prefect.deployments import Deployment
from flow import main
from prefect.filesystems import Azure
from prefect.infrastructure import KubernetesJob
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

az_block = Azure.load("twentysix")

adhoc_deployment = Deployment.build_from_flow(
    flow=main,
    name="Adhoc K8Job sidecar",
    version="1",
    storage=az_block,
    infra_overrides={"image": "radbrt/prefect_azure:latest", "namespace": "prefect2"},
    work_queue_name="kubernetes",
    path=os.getcwd()[os.getcwd().find("orion_flows"):],
)


adhoc_deployment.apply()
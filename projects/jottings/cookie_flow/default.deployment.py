from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.orion.schemas.schedules import CronSchedule
import os

# Import flow function from flow.py
from flow import cookie_flow

az_block = Azure.load("twentysix")

cookie_flow_deployment = Deployment.build_from_flow(
    flow=cookie_flow,
    name="Default Deployment",
    version="1",
    storage=az_block,
    infra_overrides={"image": "radbrt/prefect_azure:latest", "namespace": "prefect2"},
    work_queue_name="kubernetes",
    path=os.getcwd()[os.getcwd().find("orion_flows"):],
)


cookie_flow_deployment.apply()
from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.server.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import dolly_slackbot

deployment_name = "Default"

flow_name = dolly_slackbot.name
storage_path = deployment_name.lower().replace(" ", "_") + flow_name.lower().replace(" ", "_") + '/'


az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("orion-dolly")

dolly_slackbot_deployment = Deployment.build_from_flow(
    flow=dolly_slackbot,
    name=deployment_name,
    version="1",
    storage=az_block,
    infra_overrides = {
        "customizations": [
            {
                "op": "add",
                "path": "/spec/template/spec/resources",
                "value": {
                "limits": {
                    "memory": "10Gi",
                    "cpu": "4000m"
                },
                "requests": {
                    "memory": "8Gi",
                    "cpu": "3000m"
                }
                }
            }
        ]
	},
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path=storage_path,
)


dolly_slackbot_deployment.apply()
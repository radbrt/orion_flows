from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import {{ cookiecutter.flow_slug }}

deployment_name = "Default"

flow_name = {{ cookiecutter.flow_slug }}.name
storage_path = deployment_name.lower().replace(" ", "_") + flow_name.lower().replace(" ", "_") + '/'


az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("simple")

{{ cookiecutter.flow_slug }}_deployment = Deployment.build_from_flow(
    flow={{ cookiecutter.flow_slug }},
    name=deployment_name,
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path=storage_path,
)


{{ cookiecutter.flow_slug }}_deployment.apply()
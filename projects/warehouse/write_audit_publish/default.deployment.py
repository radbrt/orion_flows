from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import write_audit_publish

deployment_name = "Default"

flow_name = write_audit_publish.name
storage_path = deployment_name.lower().replace(" ", "_") + flow_name.lower().replace(" ", "_") + '/'


az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("base")

write_audit_publish_deployment = Deployment.build_from_flow(
    flow=write_audit_publish,
    name=deployment_name,
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path=storage_path,
)


write_audit_publish_deployment.apply()
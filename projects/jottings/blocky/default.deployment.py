from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.orion.schemas.schedules import CronSchedule
from prefect.infrastructure.kubernetes import KubernetesJob
import os

# Import flow function from flow.py
from flow import blocky

az_block = Azure.load("twentysix")
kubernetes_job_block = KubernetesJob.load("logging-test")

infra_overrides={ 
    "customizations": [
        {
            "op": "add",
            "path": "/spec/template/spec/volumes/-",
            "value": {
                "name": "my-volume",
                "persistentVolumeClaim": {
                    "claimName": "my-pvc"
                }
            }
        },
        {
            "op": "add",
            "path": "/spec/template/spec/containers/0/volumeMounts/-",
            "value": {
                "name": "my-volume",
                "mountPath": "/path/to/mount"
            }
        }
    ]
}

blocky_deployment = Deployment.build_from_flow(
    flow=blocky,
    name="Default Deployment",
    version="1",
    storage=az_block,
    infrastructure=kubernetes_job_block,
    work_queue_name="kubernetes",
    path=os.getcwd()[os.getcwd().find("orion_flows"):],
    infra_overrides=infra_overrides
)


blocky_deployment.apply()
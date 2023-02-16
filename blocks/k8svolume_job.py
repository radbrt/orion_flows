from prefect.infrastructure import KubernetesJob
from prefect.infrastructure.kubernetes import KubernetesImagePullPolicy

namespace = "prefect2"
image_name = "cocerxkubecr.azurecr.io/orion_meltano:latest"

customizations = [
    {
        "op": "add",
        "path": "/spec/template/spec/volumes/-",
        "value": {
            "name": "logs-data",
            "persistentVolumeClaim": {
                "claimName": "meltano-logs"
            }
        }
    },
    {
        "op": "add",
        "path": "/spec/template/spec/containers/0/volumeMounts/-",
        "value": {
            "name": "logs-data",
            "mountPath": "/logs"
        }
    }
]

k8s_job = KubernetesJob(
        namespace=namespace,
        image=image_name,
        image_pull_policy=KubernetesImagePullPolicy.ALWAYS,
        finished_job_ttl=300,
        job_watch_timeout_seconds=600,
        pod_watch_timeout_seconds=600,
        service_account_name="prefect-server",
        customizations=customizations,
    )
k8s_job.save("k8slog")
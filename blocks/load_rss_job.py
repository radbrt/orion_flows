from prefect.infrastructure import KubernetesJob
from prefect.infrastructure.kubernetes import KubernetesImagePullPolicy

namespace = "prefect2"
image_name = "cocerxkubecr.azurecr.io/orion_load_rss:latest"


k8s_job = KubernetesJob(
        namespace=namespace,
        image=image_name,
        image_pull_policy=KubernetesImagePullPolicy.ALWAYS,
        finished_job_ttl=300,
        job_watch_timeout_seconds=600,
        pod_watch_timeout_seconds=600,
    )

k8s_job.save("load-rss", overwrite=True)

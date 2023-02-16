"""
To add MY_API_TOKEN as an environment variable
- name: MY_API_TOKEN
  valueFrom:
    secretKeyRef:
      name: the-secret-name
      key: api-token
"""
from prefect.infrastructure import KubernetesJob

k8s_job = KubernetesJob(
    namespace="prefect2",
    image="cocerxkubecr.azurecr.io/orion_meltano:latest",
    job_watch_timeout_seconds=480,
    image_pull_policy="Always",
    finished_job_ttl=300,
    customizations=[
        {
            "op": "add",
            "path": "/spec/template/spec/containers/0/env/-",
            "value": {
                "name": "MY_API_TOKEN",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "k8smeltano",
                        "key": "api-key",
                    }
                },
            },
        },
        {
            "op": "add",
            "path": "/spec/template/spec/containers/0/env/-",
            "value": {
                "name": "DD_LOGS_ENABLED",
                "value": "true"
            },
        }
    ],
)
k8s_job.save("meltano-dd", overwrite=True)
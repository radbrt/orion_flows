from prefect_azure.container_instance import AzureContainerInstanceJob
from prefect_azure.container_instance import AzureContainerInstanceCredentials
from prefect.infrastructure.docker import DockerRegistry
import os

acisp = AzureContainerInstanceCredentials.load("aci-sp")
acr = DockerRegistry.load("cerxco-acr")

subscription_id = os.getenv("SUBSCRIPTION_ID")
azi = AzureContainerInstanceJob(
    name="aci-meltano",
    image="cocerxkubecr.azurecr.io/orion_meltano:latest",
    cpu=1,
    memory=1,
    aci_credentials=acisp,
    subscription_id=subscription_id,
    resource_group_name="aci-rg",
    task_start_timeout_seconds=480,
    image_registry=acr,
    identities=[f"/subscriptions/{ subscription_id }/resourcegroups/aci-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/orionid"]
)

azi.save('aci-meltano', overwrite=True)
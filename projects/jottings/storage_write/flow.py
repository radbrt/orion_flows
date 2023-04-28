from prefect import task, flow
from prefect import get_run_logger
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

@task
def write_file_to_azure_storage(storage_account_name, container_name):
    """Write a file to Azure Blob Storage"""

    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="file.txt")
    blob_client.upload_blob("Sample file content")


def az_secret(secret_name) -> str:
    kv_url = "https://co-cerx-aks-kv.vault.azure.net/"

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_url, credential=credential)
    kv_secret = client.get_secret(secret_name).value
    return kv_secret


@task
def demo_integration():
    logger = get_run_logger()
    testsecret = az_secret("testsecret")
    logger.info(f"Connected to Azure Key Vault and retrieved secret 'testsecret' with value '{testsecret}'")


@flow
def storage_write(name="Storage Write"):
    """Write a file to Azure Blob Storage"""

    storage_account_name = "cocerxsftp"
    container_name = "upl"
    demo_integration()

    write_file_to_azure_storage(storage_account_name, container_name)

if __name__ == '__main__':
    storage_write()



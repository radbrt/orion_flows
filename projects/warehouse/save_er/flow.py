from prefect import task, flow
from prefect import get_run_logger
import requests
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, WorkloadIdentityCredential
from azure.storage.blob import BlobServiceClient, BlobClient
import datetime

@task
def save_file_to_storage(prefix, url):
    filename = f"{prefix}/{str(datetime.date.today())}.json"

    cred = WorkloadIdentityCredential(resource_id="https://storage.azure.com/")
    credential = ManagedIdentityCredential(client_id="1cf29abb-1400-4d0d-aa4a-a1796f47af2a")
    service = BlobServiceClient(account_url=f"https://radlake.blob.core.windows.net/", credential=credential)

    container_client = service.get_container_client("enhetsregisteret")
    blob = BlobClient(account_url=f"https://radlake.blob.core.windows.net/", container_name="enhetsregisteret", blob_name="testfile.txt", credential=credential)
    blob_client = container_client.get_blob_client(filename)
    r = requests.get(url).raw.read()
    blob_client.upload_blob(r, blob_type="BlockBlob")

    return filename



@flow(name="Save ER")
def save_er(urls=[
        {'entity': 'foretak', 'url': "https://data.brreg.no/enhetsregisteret/api/enheter/lastned"},
        {'entity': 'virksomheter', 'url': "https://data.brreg.no/enhetsregisteret/api/underenheter/lastned"}
        ]):

    for url in urls:
        filename = save_file_to_storage(url['entity'], url['url'])


if __name__ == '__main__':
    save_er()



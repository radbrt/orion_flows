from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas, generate_container_sas, ContainerSasPermissions
from prefect.blocks.system import Secret
from prefect import task, flow
from sqlalchemy import create_engine
import json

@task
def generate_sas(account_url):
    subscription_id = Secret('subscription_id').get()
    creds = DefaultAzureCredential()
    bsc = BlobServiceClient(account_url=account_url, credential=creds)

    smc = StorageManagementClient(creds, subscription_id=subscription_id)
    nk = smc.storage_accounts.list_keys(resource_group_name='analytics', account_name='radlake')

    sas_token = generate_account_sas(
                bsc.account_name,
                account_key=nk.keys[0].value,
                resource_types=ResourceTypes(object=True, container=True, ),
                permission=AccountSasPermissions(read=True, write=True, delete=True, list=True, add=True, create=True, update=True, process=True),
                expiry=datetime.utcnow() + timedelta(days=1)
            )


@task
def renew_stage(stage_name, sas_token):
    snowflake_creds_str = Secret.load("snowflake")
    creds = json.loads(snowflake_creds_str.get())

    connectstring = f"snowflake://{creds['USER']}:{creds['PASSWORD']}@{creds['HOST']}/?role=ACCOUNTADMIN"
    engine = create_engine(connectstring)

    fileformat_query = f"""
        CREATE OR REPLACE FILE FORMAT dbthouse.dwh.dask_parquet
        TYPE = 'PARQUET';
    """

    stage_query = f"""
        CREATE OR REPLACE STAGE {stage_name}
        URL = 'azure://radlake.blob.core.windows.net/work/dask_parquet/'
        FILE_FORMAT = dbthouse.dwh.dask_parquet
        credentials = (AZURE_SAS_TOKEN='{sas_token}');
    """

    engine.execute(fileformat_query)
    engine.execute(stage_query)


@flow
def main():
    account_url = Secret.load("sf-storage-blob").get()
    stage_name = 'dbthouse.dwh.dask_stage'
    stage_sas = generate_sas(account_url)
    renew_stage(stage_name, stage_sas)




from unicodedata import name
from prefect import task, flow, get_run_logger
from prefect.deployments import DeploymentSpec
from prefect.flow_runners import KubernetesFlowRunner
import json
import pandas as pd
import feedparser
from google.oauth2 import service_account
import datetime
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from prefect.filesystems import Azure
from prefect.blocks.system import Secret


def az_secret(secret_name):
    kv_url_block = Secret.load("kv-url")
    kv_url = kv_url_block.get()

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_url, credential=credential)
    retrieved_secret = client.get_secret(secret_name)
    return retrieved_secret.value


@task
def save_frontpage():
    logger = get_run_logger()

    logger.info("Starting save frontpage")
    # gcp_key = az_secret("GCP-KEY")

    # URL = 'https://www.aftenposten.no/rss'
    # nrk_rss = feedparser.parse(URL)
    # rss_entries_string = json.dumps(nrk_rss['entries'])
    # rss_entries_json = json.loads(rss_entries_string)

    # logger.info(f"Request returned with { len(rss_entries_json) } entries")

    # credentials = service_account.Credentials.from_service_account_info(json.loads(gcp_key))
    # df = pd.DataFrame(rss_entries_json, dtype='str')
    # df['loaded_at'] = datetime.datetime.utcnow()

    #df.to_gbq("radwarehouse.staging.aftenposten_frontpage", "radwarehouse", if_exists='append', credentials=credentials)
    logger.info("Finished writing to BQ")



@flow(name="Aftenposten feed flow")
def ap_feed_flow():
    save_frontpage()


# Azure/codestore
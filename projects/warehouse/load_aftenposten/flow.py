from prefect import task, flow
from prefect import get_run_logger
import json
import pandas as pd
import feedparser
from google.oauth2 import service_account
import datetime
from prefect.blocks.system import Secret
from prefect.blocks.system import String

@task
def save_frontpage():
    gcp_key_str = Secret.load("gcp-key").get()
    gcp_key = json.loads(gcp_key_str)
    
    URL = 'https://www.aftenposten.no/rss'
    nrk_rss = feedparser.parse(URL)
    rss_entries_string = json.dumps(nrk_rss['entries'])
    rss_entries_json = json.loads(rss_entries_string)

    logger = get_run_logger()

    credentials = service_account.Credentials.from_service_account_info(gcp_key)
    df = pd.DataFrame(rss_entries_json, dtype='str')
    df['loaded_at'] = datetime.datetime.utcnow()

    df.to_gbq("radwarehouse.staging.aftenposten_frontpage", "radwarehouse", if_exists='append', credentials=credentials)

@flow(name="Load Aftenposten")
def load_aftenposten():
    save_frontpage()

if __name__ == '__main__':
    load_aftenposten()



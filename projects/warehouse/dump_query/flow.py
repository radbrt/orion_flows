from sqlalchemy import create_engine
from prefect import flow, task, get_run_logger
import random
import string
from uuid import uuid4
import json
from prefect.blocks.system import Secret


@task
def dump_table(table_name):
    logger = get_run_logger()
    logger.info(f"Dumping {table_name}")
    random_uuid = uuid4()
    logger.info(f"Random UUID: {random_uuid}")
    dump_sql = f"""
        COPY INTO @dbthouse.dwh.dask_stage/table_name/{random_uuid} FROM (
            SELECT * FROM {table_name}
        )
    """
    snowflake_creds_str = Secret.load("snowflake")
    creds = json.loads(snowflake_creds_str.get())
    connectstring = f"snowflake://{creds['USER']}:{creds['PASSWORD']}@{creds['HOST']}/?role=ACCOUNTADMIN"
    engine = create_engine(connectstring)
    engine.execute(dump_sql)
    return random_uuid


@flow
def dump_flow():
    returned_uuid = dump_table("NAV_JOB_ADS_API")
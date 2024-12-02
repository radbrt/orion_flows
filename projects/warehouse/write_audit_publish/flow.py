from prefect import task, flow, pause_flow_run, context, settings
from prefect import get_run_logger
from enum import Enum
import random
from prefect_dbt.cli.commands import DbtCoreOperation
from prefect.blocks.notifications import SlackWebhook
from snowflake.sqlalchemy import URL
from prefect_snowflake import SnowflakeCredentials
from sqlalchemy import create_engine
import pandas as pd
from prefect.artifacts import create_markdown_artifact


@flow
def trigger_dbt_flow() -> str:
    result = DbtCoreOperation(
        commands=["dbt run"],
        project_dir="/dbt",
        profiles_dir="PROFILES-DIRECTORY-PLACEHOLDER"
    ).run()
    return result

class Approve(Enum):
    YES = "Yes"
    NO = "No"

@task
async def classify() -> float:
    return round(random.random()*1000, 2)


@task
def difference_report():
    snowflake_credentials = SnowflakeCredentials.load("sfcreds")
    url = URL(
        account=snowflake_credentials.account,
        user=snowflake_credentials.user,
        password=snowflake_credentials.password,
        database="DBTHOUSE",
        warehouse="DBT_WH",
        schema="DWH",
    )

    engine = create_engine(url)

    query = """
    WITH prod AS (
        SELECT 
            year(ORDER_DATE) AS year,
            month(ORDER_DATE) AS month,
            COUNT(1) AS n_rows,
            SUM(AMOUNT) AS total_amount
        FROM dbthouse.dwh.sales
        GROUP BY 1, 2
    ),
    dev AS (
        SELECT 
            year(ORDER_DATE) AS year,
            month(ORDER_DATE) AS month,
            COUNT(1) AS n_rows,
            SUM(AMOUNT) AS total_amount
        FROM dbthouse.develop.sales
        GROUP BY 1, 2
    ),
    joined AS (
        SELECT 
            COALESCE(prod.year, dev.year) AS year,
            COALESCE(prod.month, dev.month) AS month,
            prod.n_rows AS previous_number_of_rows,
            prod.total_amount AS previous_total_amount,
            dev.n_rows AS new_number_of_rows,
            dev.total_amount AS new_total_amount
        FROM prod
        FULL JOIN dev
        ON prod.year = dev.year AND prod.month = dev.month
    )
"""
    df = pd.read_sql(query, engine)

    pd_table = df.to_markdown()

    markdown_content = f"""
# Difference Report

Comparison of production and development data:

{pd_table}
"""

    create_markdown_artifact(markdown_content, "data_qa_report", "Pre-publish difference report")

    return markdown_content

@task
def publish():
    snowflake_credentials = SnowflakeCredentials.load("sfcreds")
    url = URL(
        account=snowflake_credentials.account,
        user=snowflake_credentials.user,
        password=snowflake_credentials.password,
        database="DBTHOUSE",
        warehouse="DBT_WH",
        schema="DWH",
    )

    engine = create_engine(url)

    query = """
    ALTER SCHEMA dbthouse.develop SWAP WITH dbthouse.dwh
    """

    with engine.connect() as conn:
        conn.execute(query)



@flow(name="Write Audit Publish")
async def write_audit_publish():
    number_to_publish = await classify()
    decision = await pause_flow_run(wait_for_input=Approve)
    flow_run = context.get_run_context().flow_run
    flow_run_url = (
                f"{settings.PREFECT_UI_URL.value()}/flow-runs/flow-run/{flow_run.id}"
            )
    slack_webhook_block = SlackWebhook.load("radbrt")
    slack_webhook_block.notify("Hello from Prefect!")
    logger = get_run_logger()
    if decision == Approve.YES:
        logger.info(f"Publishing new data to the world!")


if __name__ == '__main__':
    write_audit_publish()


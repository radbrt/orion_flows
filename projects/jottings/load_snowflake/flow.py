from prefect import task, flow
from prefect import get_run_logger
import prefect
from prefect.blocks.notifications import SlackWebhook
from dask_snowflake import read_snowflake
import json
from prefect.blocks.system import Secret
import random
import string

@task()
def query_snowflake(table_name):

    snowflake_creds_str = Secret.load("snowflake").get()
    creds = json.loads(snowflake_creds_str)

    logger = get_run_logger()
    username = creds["USER"]
    password = creds["PASSWORD"]
    account = creds["HOST"]
    warehouse = 'COMPUTE_WH'
    role = creds["ROLE"]
    db = "ECONOMY_DATA_ATLAS"
    schema = "ECONOMY"

    example_query = f"""
        select *
        from {db}.{schema}.{table_name};
    """

    ddf = read_snowflake(
        query=example_query,
        connection_kwargs={
            "user": username,
            "password": password,
            "account": account,
            "warehouse": warehouse
        },
    ).repartition("32MB")
    logger.info(f"Query result has {ddf.npartitions} partitions")
    return ddf

def write_partition(df, table_name, connstr):
    df.to_sql(name='test', con=connstr, if_exists='append', index=False, sche=df)

@task()
def write_to_pg(df, to_table):

    pg_creds_str = Secret.load("pg-creds").get()
    pg_creds = json.loads(pg_creds_str)

    username = pg_creds["USERNAME"]
    password = pg_creds["PASSWORD"]
    host = pg_creds["HOST"]
    randid = ''.join(random.choices(string.ascii_uppercase, k=8))

    connstring = f"postgresql+psycopg2://{username}:{password}@{host}:5432/postgres?sslmode=require"

    df.to_sql(name=randid, uri=connstring, chunksize=1000, if_exists="replace")

    logger = get_run_logger()
    logger.info(df.dtypes)
    sum_value = df.count().compute()
    logger.info(f"Counted {sum_value} rows")

    slack_webhook_block = SlackWebhook.load("radbrt")
    slack_webhook_block.notify("Written to Postgres!")
    return sum_value


@flow
def main(table_name="MEI"):
    to_table = "ECONOMY_DATASETS"

    df = query_snowflake(table_name)
    write = write_to_pg(df, to_table)


if __name__ == '__main__':
    main()



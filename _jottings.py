#%%
from prefect import task, flow
from prefect.blocks.system import Secret
from prefect import get_run_logger
import json

@task
def stuff():
    secret = Secret.load("snowflake")
    secret_value = secret.get()

    secret_dict = json.loads(secret_value)
    secret_user = secret_dict['USER']
    logger = get_run_logger()
    logger.info(f"Secret value is { secret_user }")
    return secret_value


@flow
def some_flow():
    stuff()


if __name__=='__main__':
    some_flow()

#%%


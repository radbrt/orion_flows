from prefect import task, flow
from prefect import get_run_logger
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from prefect.blocks.system import Secret

from prefect.blocks.system import String


@task 
def az_secret(secret_name) -> str:
    kv_url = String.load("kv-url")

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_url, credential=credential)
    kv_secret = client.get_secret(secret_name).value
    return kv_secret

@task
def say_hi():
    logger = get_run_logger()
    string_block = String.load("testtext")

    logger.info("Hello Universe!")
    logger.info(string_block)
    logger.info(string_block.value)
    logger.info(dir(string_block))


@task
def print_platform_info():
    some_secret = az_secret("testsecret").run()
    logger = get_run_logger()
    logger.info(f"Launching in Kubernetes")
    logger.info(f"Secret is {some_secret}")


@flow
def blocky(name="blocky"):
    say_hi()
    print_platform_info()
    say_hi()
    print_platform_info()
    hi = say_hi()
    print_platform_info(wait_for=[hi])

if __name__ == '__main__':
    blocky()



from prefect import task, flow
from prefect import get_run_logger
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential, DefaultAzureCredential
import uuid
from prefect.blocks.system import Secret
import os
from prefect.blocks.system import String


def az_secret(secret_name) -> str:
    kv_url = String.load("kv-url").value

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_url, credential=credential)
    kv_secret = client.get_secret(secret_name).value
    return kv_secret


@task
def say_hi():
    logger = get_run_logger()
    d = os.getenv("DUMMY")
    logger.info(f"Test env: { d }")
    string_block = String.load("testtext")

    logger.info("Hello Universe!")
    logger.info(string_block)
    logger.info(string_block.value)
    logger.info(dir(string_block))


@task
def print_platform_info():
    some_secret = az_secret("testsecret")
    logger = get_run_logger()
    logger.info(f"Launching in Kubernetes")
    logger.info(f"Secret is {some_secret}")

@flow
def write_to_file():
    string_block = String.load("testtext")
    logger = get_run_logger()

    filename = f"/logs/{uuid.uuid4()}.txt"
    with open(filename, "w") as f:
        f.write(string_block.value)

    # list files in /logs
    import os
    for file in os.listdir("/logs"):
        logger.info(file)



@flow
def blocky(name="blocky"):
    say_hi()
    print_platform_info()

if __name__ == '__main__':
    blocky()



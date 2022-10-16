from prefect import task, flow
from prefect import get_run_logger
import prefect
from prefect.blocks.notifications import SlackWebhook
from prefect.filesystems import Azure
from prefect.deployments import Deployment

@task
def say_hi():
    logger = get_run_logger()
    logger.info("Hello Universe!")

    slack_webhook_block = SlackWebhook.load("radbrt")
    slack_webhook_block.notify("Hello from Prefect!")


@task
def print_platform_info():
    logger = get_run_logger()
    logger.info(f"Launching in Kubernetes")


@flow
def main_hello_flow():
    hi = say_hi()
    print_platform_info(wait_for=[hi])

if __name__ == '__main__':
    main_hello_flow()



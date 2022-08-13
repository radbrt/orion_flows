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
def hello_flow():
    hi = say_hi()
    print_platform_info(wait_for=[hi])

# if __name__ == '__main__':
#     hello_flow()


storage = Azure.load("cloudio") # load a pre-defined block


deployment = Deployment(
    flow_name="hello_flow",
    name="hello-flow-directbuild",
    version="2",
    tags=["dev"],
    storage=storage,
    infra_overrides={"image": "radbrt/prefect_azure:latest", "namespace": "prefect2"},
    schedule = prefect.orion.schemas.schedules.CronSchedule(cron="0 0 * * *")
)

deployment.build_from_flow(hello_flow)
deployment.apply()
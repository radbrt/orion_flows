from prefect import task, flow, pause_flow_run
from prefect import get_run_logger
from enum import Enum
import random
from prefect_dbt.cli.commands import DbtCoreOperation

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


@flow(name="Write Audit Publish")
async def write_audit_publish():
    number_to_publish = await classify()
    decision = await pause_flow_run(wait_for_input=Approve)
    logger = get_run_logger()
    if decision == Approve.YES:
        logger.info(f"Publishing {number_to_publish} to the world!")

if __name__ == '__main__':
    write_audit_publish()


from prefect import task, flow
from prefect import get_run_logger
from prefect.client import get_client
from prefect.server.schemas.schedules import CronSchedule
import datetime


@task
async def update_schedule(
    flow_name: str, deployment_name: str, schedule
) -> None:
    """Update the schedule of a deployment"""
    async with get_client() as client:
        try:
            deployment = await client.read_deployment_by_name(
                f"{flow_name}/{deployment_name}"
            )
        except:
            raise ValueError(
                f"Could not find deployment with name {deployment_name} for flow {flow_name}"
            )
        logger = get_run_logger()
        logger.info(f"Redeploying deployment: {deployment}")

        # deployment is updated if deployment with the same name and flow_id already exists
        await client.create_deployment(
            name=deployment.name,
            flow_id=deployment.flow_id,
            schedule=schedule,
        )

@task
async def run_once(flow_name, deployment_name):
    """Trigger a deployment to run once"""
    async with get_client() as client:
        try:
            deployment = await client.read_deployment_by_name(
                f"{flow_name}/{deployment_name}"
            )
        except:
            raise ValueError(
                f"Could not find deployment with name {deployment_name} for flow {flow_name}"
            )
    
        rr = await client.create_flow_run_from_deployment(deployment.id)



@flow(name="Reschedule")
def reschedule():
    """Run flow and reschedule"""
    flow_name = "update-unemployment-report"
    deployment_name = "Report"
    
    run_once(flow_name, deployment_name)

    new_schedule = CronSchedule(cron="0 9 * * 1-5")
    update_schedule(flow_name, deployment_name, new_schedule)
    

if __name__ == '__main__':
    reschedule()



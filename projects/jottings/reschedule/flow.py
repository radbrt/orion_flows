from prefect import task, flow
from prefect import get_run_logger
from prefect import get_client
from prefect.server.schemas.schedules import CronSchedule
import datetime
from prefect.deployments import run_deployment
from prefect.states import Scheduled


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

        # deployment is updated if deployment with the same name and flow_id already exists
        await client.create_deployment(
            name=deployment.name,
            flow_id=deployment.flow_id,
            schedule=schedule,
        )

@task
async def run_once(flow_name, deployment_name):
    """Trigger a deployment to run once"""
    dt = datetime.datetime(2024, 1, 2)
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

        logger.info(f"Creating flow run for deployment {deployment.name}, id: {deployment.id}")
        logger.info(f"The flow will be scheduled to run at {dt}")
        await client.create_flow_run_from_deployment(str(deployment.id), state=Scheduled(scheduled_time=dt))


@task
def simple_run(full_name):
    """Trigger a deployment to run once, as a subflow"""
    flow_run = run_deployment(full_name, scheduled_time=datetime.datetime.utcnow())



@flow(name="Reschedule")
def reschedule():
    """Run flow and reschedule"""
    flow_name = "Logging Flow"
    deployment_name = "Default"
    full_name = f"{flow_name}/{deployment_name}"
    
    # Trigger Deployment to run once, async
    # run_once(flow_name, deployment_name)

    # Update schedule for deployment
    # new_schedule = CronSchedule(cron="0 9 * * 1-5")
    # new_schedule = [datetime.datetime.utcnow() + datetime.timedelta(seconds=1000)]
    # update_schedule(flow_name, deployment_name, new_schedule)

    # Trigger Deployment to run as subflow
    simple_run(full_name)


if __name__ == '__main__':
    reschedule()



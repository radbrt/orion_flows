# Schedule and run deployments from a flow

Sometimes, you need to run or perhaps schedule a flow from another flow. If you just need to run a flow, and it can run on the same infrastructure that your current flow is running on, it might be useful to import the flow in python. That requires that you have the code handy though, so that you can import it in python - something like `from my_flows import some_flow`.

But you don't always have access to the code, so what can you do? One option is to call the Prefect REST API. But since you are inside a flow, an even better approach is to call it natively from python.

## Subflow
One option is to run the deployment as a regular subflow - except possibly on different infrastructure.

```py
from prefect.deployments import run_deployment
import datetime

flow_name = "update-unemployment-report"
deployment_name = "Report"
full_name = f"{flow_name}/{deployment_name}"

flow_run = run_deployment(full_name, scheduled_time=datetime.datetime.utcnow())
```

Notice that you have to declare a `scheduled_time` - you can set this ahead in time, in which case your flow will keep running just waiting for the subflow to start. So for most practical purposes, maybe setting scheduled time to now (in UTC) is the best option.

## Kick off deployment async

If you don't want the flow to run as a subflow, you can trigger a deployment via the prefect `context` object.

```py
from prefect import task
from prefect.client import get_client

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
```

Note that this function needs to be async. This will create a new run of the deployment. You will find it in the Prefect UI, but your currently running flow will not keep track of it.


## Create/Schedule a deployment

Maybe you want to schedule a flow for later? Create a new deployment or overwrite an existing one, with a new schedule.

```py
from prefect import task
from prefect.client import get_client

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
```

If the deployment already exists, it will be overwritten.


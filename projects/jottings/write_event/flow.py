from prefect import task, flow
from prefect import get_run_logger
from prefect.events.utilities import emit_event
import datetime
import uuid

@task
def say_hi():
    logger = get_run_logger()
    event_name = 'test-event'
    resource = {'prefect.resource.id': 'eventbased-lineage',
                'prefect.resource.name': 'eventbased-lineage'}
    
    occured = datetime.datetime.utcnow().isoformat()
    uid = str(uuid.uuid4())
    payload = {'message': 'Hello, world!'}
    emit_event(
        event=event_name,
        resource=resource,
        occurred=occured,
        payload=payload,
        id=uid
    )


@flow(name="Write Event")
def write_event():
    say_hi()

if __name__ == '__main__':
    write_event()



from prefect import task, flow
from prefect import get_run_logger
from prefect_shell import ShellOperation


@flow(name="Logging Flow")
def logging_flow(x=1, y=2):

    ShellOperation(
        commands=[
            f"python logging_script.py"
        ],
        stream_output=True,
    ).run()

if __name__ == '__main__':
    logger = get_run_logger()
    logger.info("starting flow")
    logging_flow(x=2, y=4)



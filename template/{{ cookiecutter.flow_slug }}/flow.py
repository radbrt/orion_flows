from prefect import task, flow
from prefect import get_run_logger


@task
def say_hi():
    logger = get_run_logger()
    logger.info("Hello Universe!")


@task
def print_platform_info():
    logger = get_run_logger()
    logger.info(f"Launching in Kubernetes")


@flow(name="{{ cookiecutter.flow_name }}")
def {{ cookiecutter.flow_slug }}():
    say_hi()
    print_platform_info()
    say_hi()
    print_platform_info()
    hi = say_hi()
    print_platform_info(wait_for=[hi])

if __name__ == '__main__':
    {{ cookiecutter.flow_slug }}()



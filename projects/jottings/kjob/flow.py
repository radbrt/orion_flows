from kubernetes import client, config, utils, watch
import sys
import kubernetes.client
from kubernetes.client.rest import ApiException
from time import sleep
from prefect import task, flow, get_run_logger
# Setup K8 configs
import random
import string


def id_generator(size=12, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



def kube_create_job_object():

    container = client.V1Container(
        name='busybox',
        image='busybox',
        args=["/bin/sh", "-c", "sleep 10; echo 'Hello World'"],
    )
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'name': 'simple-job'}),
        spec=client.V1PodSpec(restart_policy='OnFailure', containers=[container]))
    # Create the specification of deployment
    spec = client.V1JobSpec(template=template)
    # Instantiate the job object
    job = client.V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=client.V1ObjectMeta(name='sidecar-job', namespace='prefect2'),
        spec=spec)

    return job


@task
def check_config():

    configuration = config.load_incluster_config()
    api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(configuration))
    logger = get_run_logger()

    try: 
        api_response = api_instance.get_api_resources()
        logger.info(api_response)
    except ApiException as e:
        print("Exception when calling API: %s\n" % e)

@task
def kube_create_job(api_instance):
    # Create the job definition
    logger = get_run_logger()
    name = id_generator()
    body = kube_create_job_object()
    try: 
        api_response = api_instance.create_namespaced_job("prefect2", body, pretty=True)
        logger.info(api_response)
        logger.info(dir(api_response))
        v1 = client.CoreV1Api()
        w = watch.Watch()
        for e in w.stream(v1.read_namespaced_pod_log, name=pod, namespace=namespace):
            print(e)
        sleep(10)
        logger.info("Sleeping 10 seconds")
        job_log = api_instance.read_namespaced_pod_log(name=name, namespace='prefect2')
        logger.info(job_log)
    except ApiException as e:
        print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
    return

@flow
def main():
    check_config()
    api_instance = kubernetes.client.BatchV1Api()
    kube_create_job(api_instance)

if __name__=='__main__':
    main()

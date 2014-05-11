from time import sleep

from celery import task


@task
def celery_task():
    sleep(3)
    return 'Working!'

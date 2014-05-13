from time import sleep

from celery import task

from app.models import Dynamic


@task
def celery_task():
    sleep(3)
    return 'Working!'

# @task
# def main(dynamic):
#

# -*- coding: utf-8 -*-
rootPath = '/home/evolution/PycharmProjects/celery_project/programs/'
exchange = 'first'
broker_url='amqp://test:test@localhost:5672/'
result_backend='redis://localhost/2'
numprocs=2
# result_backend='db+mysql://root:brave@localhost/celery_failure_task'
# result_backend='elasticsearch://es1:9200/celery_task/taskinfo'
broker_url='amqp://test:test@localhost:5672/first'
result_backend='redis://localhost/2'
# result_backend='db+mysql://root:brave@localhost/celery_failure_task'
# result_backend='elasticsearch://es1:9200/celery_task/taskinfo'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
include = ['fast.task']
task_queues = {
    'fastemail': {
        'exchange': 'first',
        'routing_key': 'fastemail',
    },
}
task_routes = {
    'fast.task.handler': {'queue': 'fastemail', 'exchange': 'first', 'routing_key': 'fastemail'},
}

#task result set
result_expires = 3600
result_persistent = True

#Time limit
task_time_limit = 3
task_soft_time_limit = 1

#Process limit
worker_max_tasks_per_child = 8000
#12MB
worker_max_memory_per_child = 50000

#Task Ack
task_acks_late = True
task_reject_on_worker_lost = True   # Warning Enabling this can cause message loops; make sure you know what you're doing
worker_prefetch_multiplier = 0

#Remote control
worker_pool_restarts = True
# worker_autoscaler = "10,3"  #removed in 4.x

#Only store task errors in the result backend
task_ignore_result = False
task_store_errors_even_if_ignored = True

#Remote controller default enabled
worker_enable_remote_control=True
worker_state_db='/home/evolution/PycharmProjects/celery_project/log/xin1/fast'

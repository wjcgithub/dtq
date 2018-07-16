broker_url='amqp://test:test@localhost:5672/first'
result_backend='redis://localhost/2'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
include = ['sms.task']
task_queues = {
    'xin2_sms': {
        'exchange': 'first',
        'routing_key': 'xin2_sms',
    },
}
task_routes = {
    'sms.task.handler': {'queue': 'xin2_sms', 'exchange': 'first', 'routing_key': 'xin2_sms'},
}
result_expires = 3600
result_persistent = True
task_time_limit = 5
task_soft_time_limit = 3
worker_max_tasks_per_child = 8000
worker_max_memory_per_child = 50000
task_acks_late = True
task_reject_on_worker_lost = True   # Warning Enabling this can cause message loops; make sure you know what you're doing
worker_prefetch_multiplier = 0
worker_pool_restarts = True
task_ignore_result = False
task_store_errors_even_if_ignored = True
worker_enable_remote_control=True
worker_state_db='/home/evolution/PycharmProjects/celery_project/programs/log/xin2/sms/sms'

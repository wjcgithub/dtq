# config article
# https://flower.readthedocs.io/en/latest/config.html#conf

auto_refresh=True
broker_api="http://test:test@develop:55672/api/"
basic_auth=['admin:admin','wjc:wjc']
db='flower'
inspect_timeout=60000.0
#Maximum number of workers to keep in memory (by default, max_workers=5000)
#max_workers
#Maximum number of tasks to keep in memory (by default, max_tasks=10000)
#max_tasks
#default False
persistent=True
port=5555
task_columns="name, uuid, state, args, kwargs, result, received, started, runtime"
timezone='Asia/Shanghai'
# resolve Substantial drift
event_queue_ttl=300
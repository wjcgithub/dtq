# _*_ coding:utf-8 _*_
import logging
logging.basicConfig(format='%(asctime)s %(levelname)8s: %(message)s', datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)
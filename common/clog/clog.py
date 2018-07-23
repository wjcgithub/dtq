# _*_ coding:utf-8 _*_
import logging
from celery.utils.log import get_task_logger
# use logging module for easy debug
logging.basicConfig(format='%(asctime)s %(levelname)8s: %(message)s', datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

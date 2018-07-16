#!/usr/bin/env python3.5
# _*_ coding:utf-8 _*_
from __future__ import absolute_import, unicode_literals
from celery import Celery
import sms.celeryconfig.celeryconfig as celeryconfig
import sys
import os

sys.path.append(os.path.abspath('..')+'/common')

app = Celery('sms')
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()
        
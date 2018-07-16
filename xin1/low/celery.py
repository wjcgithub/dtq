#!/usr/bin/env python3.5
# _*_ coding:utf-8 _*_
from __future__ import absolute_import, unicode_literals
from celery import Celery
import low.celeryconfig.celeryconfig as celeryconfig
import sys
import os

sys.path.append(os.getcwd()+'/../common')

app = Celery('low')
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()


from __future__ import absolute_import, unicode_literals

import errno

import requests
from celery.exceptions import Reject
from low.celery import app
from CeleryCustomTask.CeleryCustomTask import Ctask

@app.task(
          base=Ctask,
          bind=True,
          )
def handler(self, payload):
    try:
        print(payload)
        # url = 'http://local.nc.xin.com/test/celery-handler'
        # r= requests.post(url,{'payload':str},timeout=3)
        # r.raise_for_status()
        # r.json()
    except MemoryError as exc:
        raise Reject(exc, requeue=False)
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            raise Reject(exc, requeue=False)
    except Exception as exc:
        self.retry(countdown=2, exc=exc, max_retries=3)


    # try:
    #     url = 'http://local.nc.xin.com/test/celery-handler'
    #     r= requests.post(url,{'payload':str},timeout=3)
    #     r.raise_for_status()
    #     r.json()
    # except requests.RequestException as exc:
    #     raise self.retry(countdown=2, max_retries=3, exc=exc)
    # f = open('/tmp/num.txt', 'a+')
    # f.write('retry: '+params+'--pid:'+str(os.getpid())+"\r\n")
    # f.close()
    # print(str)
    # res = 1/0
    return payload
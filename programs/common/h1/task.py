from __future__ import absolute_import, unicode_literals

import errno
import requests
import json

from celery.exceptions import Reject
from h1.celery import app
from CeleryCustomTask.CeleryCustomTask import Ctask

@app.task(
          base=Ctask,
          bind=True,
          )
def handler(self, payload):
    try:
        url = 'http://local.nc.xin.com/test/celery-handler'
        r= requests.post(url,{'payload':payload},timeout=6)
        r.raise_for_status()
        data = {"queuename":"common_h1", "payload":payload}
        return json.dumps(data)
    except MemoryError as exc:
        raise Reject(exc, requeue=True)
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            raise Reject(exc, requeue=True)
    except Exception as exc:
        self.retry(countdown=3, exc=exc, max_retries=3)
        
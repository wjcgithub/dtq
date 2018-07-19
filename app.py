#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
from update_config.updateConfig import UpdateConfig

if __name__ == '__main__':
    # os.environ.setdefault('ENV', 'local')
    # print(os.environ.get('ENV'))
    u = UpdateConfig()
    u.start()

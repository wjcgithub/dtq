#!/usr/bin/env python3.5
# _*_ coding:utf-8 _*_
import os
# from config2 import config
from update_config.updateConfig import UpdateConfig

if __name__ == '__main__':
    os.environ.setdefault('ENV', 'local')
    print(os.environ.get('ENV'))
    # print(config.environ)
    u = UpdateConfig()
    u.start()

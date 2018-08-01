#!/bin/bash
#generate auth
echo -n "Please input your project root path: "
read rootpath
if [ -e $rootpath ]
then
	echo "You inputs root path is $rootpath"
	if [ ! -d $rootpath/common/celeryConfig ]
	then
		mkdir $rootpath/common/celeryConfig
		touch $rootpath/common/celeryConfig/__init__.py
              fi
else
    echo "You inputs root path not exists"
fi

#touch mysqlconfig

    if [ -e $rootpath/common/celeryConfig/mysqlconfig.py ]
    then
        echo -n "file mysqlconfig.py exists, is not overwrite? [yes/no]: "
        read op
        if [ $op = "yes" ]
        then
            cat>$rootpath/common/celeryConfig/mysqlconfig.py<<EOF
# -*- coding: utf-8 -*-
db_host = ''
db_user = ''
db_pass = ''
db_name = '3'
EOF
          fi
      else
        touch $rootpath/common/celeryConfig/mysqlconfig.py
        cat>$rootpath/common/celeryConfig/mysqlconfig.py<<EOF
    # -*- coding: utf-8 -*-
    db_host = ''
    db_user = ''
    db_pass = ''
    db_name = '2'
EOF
        fi
echo "mysqlconfig touch success"

# touch pconfig
    if [ -e $rootpath/common/celeryConfig/pconfig.py ]
    then
        echo -n "file pconfig.py exists, is not overwrite? [yes/no]: "
        read op
        if [ $op = "yes" ]
        then
            cat>$rootpath/common/celeryConfig/pconfig.py<<EOF
# -*- coding: utf-8 -*-
supervisor_config_path='/etc/supervisor/conf.d'
super_file_suffix='conf'
rootpath=''
venvpath=''
hostname=''
log_level='info'
EOF
          fi
      else
        touch $rootpath/common/celeryConfig/pconfig.py
        cat>$rootpath/common/celeryConfig/pconfig.py<<EOF
# -*- coding: utf-8 -*-
supervisor_config_path='/etc/supervisor/conf.d'
super_file_suffix='conf'
rootpath=''
venvpath=''
hostname=''
log_level='info'
EOF
        fi
echo "pconfig touch success"

#touch redisconfig

    if [ -e $rootpath/common/celeryConfig/redisconfig.py ]
    then
        echo -n "file redisconfig.py exists, is not overwrite? [yes/no]: "
        read op
        if [ $op = "yes" ]
        then
            cat>$rootpath/common/celeryConfig/redisconfig.py<<EOF
# -*- coding: utf-8 -*-
host = ''
port = 6379
db = 0
EOF
          fi
      else
        touch $rootpath/common/celeryConfig/redisconfig.py
        cat>$rootpath/common/celeryConfig/redisconfig.py<<EOF
# -*- coding: utf-8 -*-
host = ''
port = 6379
db = 0
EOF
        fi
echo "redisconfig touch success"





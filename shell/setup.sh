#!/bin/bash

# dtq setup script

checkPython()
{
    #推荐版本V2.6.5
    V1=3
    V2=5
    V3=all

    echo need python version is : $V1.$V2.$V3

    #获取本机python版本号。这里2>&1是必须的，python -V这个是标准错误输出的，需要转换
    U_V1=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $1}'`
    U_V2=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $2}'`
    U_V3=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $3}'`

    echo your python version is : $U_V1.$U_V2.$U_V3

    if [ $U_V1 -lt $V1 ];then
        echo 'Your python version is not OK!(1)'
        exit 1
    elif [ $U_V1 -eq $V1 ];then
        if [ $U_V2 -lt $V2 ];then
            echo 'Your python version is not OK!(2)'
            exit 1
        elif [ $U_V2 -eq $V2 ];then
	    if [[ $U_V3 -lt $V3 || $V3 != all ]];then
                echo 'Your python version is not OK!(3)'
                exit 1
            fi
        fi
    fi

    echo Your python version is OK!
}
checkPython

# create user
user=celery
grep "^$user:" /etc/passwd >& /dev/null
if [ $? -ne 0 ]
then
    useradd -M -s /usr/sbin/nologin $user
fi

#generate auth
echo -n "Please input your project root path: "
read rootpath
if [ -e $rootpath ]
then
	echo "You inputs root path is $rootpath"
	if [ ! -d $rootpath/log ]
	then
		mkdir $rootpath/log
	fi

	if [ ! -d $rootpath/programs ]
	then
		mkdir $rootpath/programs
	fi
		
else
	echo "You inputs root path not exists"
fi
chown $user:$user $rootpath/log
chown $user:$user $rootpath/programs

#installing packages of python3
echo -n "Please input your supervisor path of conf.d: "
read supervisorpath
if [ -d $supervisorpath ]
then
	chown root:$user $supervisorpath
else
	echo "You inputs supervisor conf.d path is not exists"
fi

# install deps
# yum install libffi-devel
# apt install libffi-dev
$pip3path install -U setuptools
yum install libffi-devel python3-dev
$pip3path install pymysql redis celery flower elasticsearch requests

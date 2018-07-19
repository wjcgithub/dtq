#!/bin/bash

# dtq setup script


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
chown root:$user /etc/supervisor/conf.d
chown $user:$user $rootpath/log
chown $user:$user $rootpath/programs

#installing packages of python3
echo -n "Please input your bin path of pip of python3: "
read pip3path
if [ -e $pip3path ]
then
	echo "You pip3 bin path is $pip3path"
	$pip3path install -U pymysql logging warnings redis celery html
else
	echo "You inputs bin path of pip not exists"
fi

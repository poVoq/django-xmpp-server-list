HOSTCMD=ssh eris
XMPPHOME=/usr/local/home/xmpplist/
GITDIR=${XMPPHOME}/xmpplist
SU=su xmpplist -s /bin/bash -c

deploy:
	git push origin master
	${HOSTCMD} "cd ${GITDIR} && sudo git pull origin master"
	${HOSTCMD} "cd ${GITDIR} && sudo bin/pip install -U -r requirements.txt"
	${HOSTCMD} "cd ${GITDIR} && sudo ${SU} 'bin/python manage.py syncdb --noinput'"
	${HOSTCMD} "cd ${GITDIR} && sudo ${SU} 'bin/python manage.py migrate'"
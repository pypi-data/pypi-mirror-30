Quickstart
^^^^^^^^^
Install dataultra-cmd from PyPI:
::

    pip install ductl

Usage
^^^^^^^^^^
1.login
login dataultra by:
::

    ductl login -u[--username] xxx -p[--password] xxx -d[--domain] huayun.com/bigdata.com -a[--address] 10.10.10.10:8080 -s[--security] http/https


or
::

    ductl login

If none is specified, linux system will check /etc/dataultractl/os-verify and windows check C:/dataultractl/os-verify
The file will be like:
::

    [verify]
    username=xxx
    password=xxx
    domain=xxx
    address=xxx
    security=xxx

#.logout
logout dataultra by:
::

    ductl logout

#.ls
list cluster/machine/application/serice/task/microservice/instance info by:
::

    duclt ls cluster [--clusterid xxx]
    duclt ls machine [--machineid xxx]
    duclt ls application [--appid xxx]
    duclt ls service --appid xxx
    duclt ls task --appid xxx
    duclt ls microservice --serviceid xxx
    duclt ls instance --serviceid xxx [--instanceid xxxx -t/-l]

#.statistics
statistics cluster/machine/application/microservice info by:
::

    duclt statistics cluster [--clusterid xxx]
    duclt statistics machine
    duclt statistics application [--appid xxx]
    duclt statistics microservice --serviceid xxx

#.deploy
deploy service/machine/task by:
::

    duclt deploy service --serviceid xxx --appid xxx
    duclt deploy machine --machineid xxx --clusterid xxx
    duclt deploy task --taskid xxx --appid xxx

#.undeploy
undeploy service/machine/instance/task by:
::

    duclt undeploy service --serviceid xxx --appid xxx
    duclt undeploy machine --machineid xxx --clusterid xxx
    duclt undeploy instance --serviceid xxx --microserviceid xxx --instanceid xxx
    duclt undeploy task --taskid xxx --appid xxx

#.start
start task by:
::

    duclt start task --taskid xxx --appid xxx

#.stop
stop task by:
::

    duclt stop task --taskid xxx --appid xxx

#.delete
delete cluster/machine/application/service/task/microservice/instance by:
::

    duclt delete cluster --clusterid xxx
    duclt delete machine --machineid xxx
    duclt delete application --appid xxx
    duclt delete service --serviceid xxx --appid xxx
    duclt delete task --taskid xxx --appid xxx
    duclt delete microservice --microserviceid xxx --serviceid xxx
    duclt delete instance --serviceid xxx --microserviceid xxx --instanceid xxx

#.remove
remove machine from cluster, by:
::

    duclt remove machine --machineid xxx --clusterid xxx

#.add
add machine to cluster, by:
::

    duclt add machine --machineid xxx ---clusterid xxx





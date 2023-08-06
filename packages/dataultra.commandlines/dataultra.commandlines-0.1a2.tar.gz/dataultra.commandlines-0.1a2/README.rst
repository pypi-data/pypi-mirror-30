Quickstart
^^^^^^^^^
Install dataultra-cmd from PyPI:
::

    pip install dataultra.commandline

Usage
^^^^^^^^^^
1.login
login dataultra by:
::

    dataultra login -u[--username] xxx -p[--password] xxx -d[--domain] huayun.com/bigdata.com -a[--address] 10.10.10.10:8080 -s[--security] http/https


or
::

    dataultra login

If none is specified, linux system will check /etc/dataultra/os-verify and windows check C:/dataultra/os-verify
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

    dataultra logout

#.ls
list cluster/machine/application/serice/task/microservice/instance info by:
::

    dataultra ls cluster [--clusterid xxx]
    dataultra ls machine [--machineid xxx]
    dataultra ls application [--appid xxx]
    dataultra ls service --appid xxx
    dataultra ls task --appid xxx
    dataultra ls microservice --serviceid xxx
    dataultra ls instance --serviceid xxx [--instanceid xxxx -t/-l]

#.statistics
statistics cluster/machine/application/microservice info by:
::

    dataultra statistics cluster [--clusterid xxx]
    dataultra statistics machine
    dataultra statistics application [--appid xxx]
    dataultra statistics microservice --serviceid xxx

#.deploy
deploy service/machine/task by:
::

    dataultra deploy service --serviceid xxx --appid xxx
    dataultra deploy machine --machineid xxx --clusterid xxx
    dataultra deploy task --taskid xxx --appid xxx

#.undeploy
undeploy service/machine/instance/task by:
::

    dataultra undeploy service --serviceid xxx --appid xxx
    dataultra undeploy machine --machineid xxx --clusterid xxx
    dataultra undeploy instance --serviceid xxx --microserviceid xxx --instanceid xxx
    dataultra undeploy task --taskid xxx --appid xxx

#.start
start task by:
::

    dataultra start task --taskid xxx --appid xxx

#.stop
stop task by:
::

    dataultra stop task --taskid xxx --appid xxx

#.delete
delete cluster/machine/application/service/task/microservice/instance by:
::

    dataultra delete cluster --clusterid xxx
    dataultra delete machine --machineid xxx
    dataultra delete application --appid xxx
    dataultra delete service --serviceid xxx --appid xxx
    dataultra delete task --taskid xxx --appid xxx
    dataultra delete microservice --microserviceid xxx --serviceid xxx
    dataultra delete instance --serviceid xxx --microserviceid xxx --instanceid xxx

#.remove
remove machine from cluster, by:
::

    dataultra remove machine --machineid xxx --clusterid xxx

#.add
add machine to cluster, by:
::

    dataultra add machine --machineid xxx ---clusterid xxx





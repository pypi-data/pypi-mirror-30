# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.commonnode import CommonNode as CN
from .v3_0.service import Service
from .v3_0.task import Task
from .v3_0.instance import Instance


class UndeployCommands(object):
    @args("--machineid", dest="machineids", required=True, nargs="+", help=u"主机ID")
    @args("--clusterid", dest="clusterid", required=True, help=u"所属集群ID")
    def machine(self, auth, machineids, clusterid):
        """主机下线"""
        CN.undeploy_batch(auth, clusterid, machineids)

    @args("--serviceid", dest="serviceids", required=True, nargs="+", help=u"服务ID")
    @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    def service(self, auth, serviceids, appid):
        """服务下线"""
        Service.undeploy_batch(auth, appid, serviceids)

    @args("--instanceid", dest="instanceids", required=True, nargs="+", help=u"实例ID")
    @args("--microserviceid", dest="microserviceid", required=True, help=u"所属微服务ID")
    @args("--serviceid", dest="serviceid", required=True, help=u"所属服务ID")
    def instance(self, auth, instanceids, microserviceid, serviceid):
        """部署实例"""
        Instance.undeploy_batch(auth, serviceid, microserviceid, instanceids)

    @args("--taskid", dest="taskids", required=True, nargs="+", help=u"任务ID")
    @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    def task(self, auth, taskids, appid):
        """任务上线"""
        Task.undeploy_batch(auth, appid, taskids)

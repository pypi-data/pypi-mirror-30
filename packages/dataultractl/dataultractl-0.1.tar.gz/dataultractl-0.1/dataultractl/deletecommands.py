# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.cluster import Cluster
from .v3_0.commonnode import CommonNode as CN
from .v3_0.application import Application
from .v3_0.service import Service
from .v3_0.task import Task
from .v3_0.microservice import MicroService
from .v3_0.instance import Instance


class DeleteCommands(object):
    @args("--clusterid", dest="clusterid", required=True, help=u"集群ID")
    def cluster(self, auth, clusterid):
        """删除集群"""
        Cluster.delete(auth, clusterid)

    @args("--machineid", dest="machineids", required=True, nargs="+", help=u"主机ID")
    def machine(self, auth, machineids):
        """删除主机"""
        CN.delete_batch(auth, machineids)

    @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    def application(self, auth, appid):
        """删除应用"""
        Application.delete(auth, appid)

    @args("--serviceid", dest="serviceids", required=True, nargs="+", help=u"服务ID")
    @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    def service(self, auth, serviceids, appid):
        """删除服务"""
        Service.delete_batch(auth, appid, serviceids)

    # @args("--taskid", dest="taskids", required=True, nargs="+", help=u"任务ID")
    # @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    # def task(self, auth, taskids, appid):
    #     """删除任务"""
    #     Task.delete_batch(auth, appid, taskids)
    @args("--taskid", dest="taskids", required=True, nargs="+", help=u"任务ID")
    def task(self, auth, taskids):
        """删除任务"""
        Task.delete_batch(auth, taskids)

    @args("--microserviceid", dest="microserviceids", required=True, nargs="+", help=u"微服务ID")
    @args("--serviceid", dest="serviceid", required=True, help=u"服务ID")
    def microservice(self, auth, microserviceids, serviceid):
        """删除微服务"""
        MicroService.delete_batch(auth, serviceid, microserviceids)

    @args("--instanceid", dest="instanceids", required=True, nargs="+", help=u"实例ID")
    @args("--microserviceid", dest="microserviceid", required=True, help=u"所属微服务ID")
    @args("--serviceid", dest="serviceid", required=True, help=u"所属服务ID")
    def instance(self, auth, instanceids, microserviceid, serviceid):
        """删除实例"""
        Instance.delete_batch(auth, serviceid, microserviceid, instanceids)


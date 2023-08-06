# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.cluster import Cluster
from .v3_0.commonnode import CommonNode as CN
from .v3_0.application import Application
from .v3_0.microservice import MicroService


class StatisCommands(object):
    @args("--clusterid", dest="clusterid", default=None, help=u"根据ID统计集群信息")
    def cluster(self, auth, clusterid=None):
        """统计集群信息"""
        if clusterid:
            Cluster.statistics_by_id(auth, clusterid)
        else:
            Cluster.statistics(auth)

    def machine(self, auth):
        """统计主机信息"""
        CN.statistic(auth)

    @args("--appid", dest="appid", default=None, help=u"根据id统计该应用信息")
    def application(self, auth, appid=None):
        """统计应用信息"""
        if appid:
            Application.statistics_by_id(auth, appid)
        else:
            Application.statistics(auth)

    @args("--serviceid", dest="serviceid", required=True, help=u"根据服务id统计该服务下的微服务信息")
    def microservice(self, auth, serviceid):
        """统计微服务信息"""
        MicroService.statistics(auth, serviceid)


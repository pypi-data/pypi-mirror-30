# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.commonnode import CommonNode as CN


class RemoveCommands(object):
    @args("--machineid", dest="machineids", required=True, nargs="+", help=u"主机ID")
    @args("--clusterid", dest="clusterid", required=True, help=u"所属集群ID")
    def machine(self, auth, machineids, clusterid):
        """移除集群中的主机"""
        CN.remove_batch(auth, clusterid, machineids)

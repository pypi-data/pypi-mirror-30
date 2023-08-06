# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.task import Task


class StartCommands(object):
    @args("--taskid", dest="taskids", required=True, nargs="+", help=u"任务ID")
    @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    def task(self, auth, taskids, appid):
        """启动任务"""
        Task.start_batch(auth, appid, taskids)

# -*- coding: utf-8 -*-
import json
import collections
from ..utils.http_utils import http_request
from ..utils.common_utils import print_table, obj_replace_time_field, status_format

lifecycle_conf = {"running": u"已上线",
                  "setting": u"配置中",
                  "executing": u"执行中"}
status_summary_conf = {"successfully_deployed": u"已上线",
                       "failed_deployed": u"上线失败",
                       "executing": u"执行中",
                       "setting": u"配置中"}
running_status_conf = {"green": u"正常",
                       "gray": u"",
                       "yellow": u"异常",
                       "red": u"错误"}


class Task(object):
    @staticmethod
    def list(auth, appid):
        """根据应用ID显示该应用下任务列表"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?application_id={}".format(security, address, "/dispatch/platform/v1/tasks", appid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"任务名"
            header["status_summary_running"] = u"当前状态"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名"
            header["version"] = u"版本"
            header["prototype"] = u"类型"
            header["cpu_allocated_total"] = u"CPU使用率（核）"
            header["memory_allocated_total"] = u"内存使用率（M）"
            header["schedule_start"] = u"任务开始时间"
            header["schedule_interval"] = u"任务间隔时间"
            header["create_time"] = u"创建时间"
            tasks_info = []
            tasks = data.get("tasks", [])
            for task in tasks:
                task["cpu_allocated_total"] = "{}/{}".format(
                    task.get("resource_info", {}).get("cpu_allocated", "NaN"),
                    task.get("resource_info", {}).get("cpu_total", "NaN"))
                task["memory_allocated_total"] = "{}/{}".format(
                    task.get("resource_info", {}).get("memory_allocated", "NaN"),
                    task.get("resource_info", {}).get("memory_total", "NaN"))
                task["schedule_start"] = task.get("schedule", {}).get("start_time", "")
                interval = task.get("schedule", {}).get("interval", {})
                task["schedule_interval"] = "{}{}".format(interval.get("value", ""), interval.get("unit", ""))
                task = obj_replace_time_field(task, ["create_time"])
                status_summary_running = status_format(task.get("lifecycle", ""), lifecycle_conf,
                                                       task.get("status_summary", ""), status_summary_conf,
                                                       task.get("running_status", ""), running_status_conf)
                task["status_summary_running"] = status_summary_running
                task_info = [task.get(key, "") for key in header]
                tasks_info.append(task_info)
            print_table(header.values(), tasks_info)
        except Exception as e:
            raise

    @staticmethod
    def deploy_batch(auth, appid, taskids):
        """任务上线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"任务 {} 上线指令发送成功".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def undeploy_batch(auth, appid, taskids):
        """任务下线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"任务 {} 下线指令发送成功".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def start_batch(auth, appid, taskids):
        """启动任务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/start")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"任务 {} 启动指令发送成功".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def stop_batch(auth, appid, taskids):
        """停止任务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/stop")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"任务 {} 停止指令发送成功".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def delete_batch(auth, taskids):
        """删除任务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/plaStform/v1/tasks")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"任务 {} 删除成功".format(','.join(taskids)))
        except Exception as e:
            raise


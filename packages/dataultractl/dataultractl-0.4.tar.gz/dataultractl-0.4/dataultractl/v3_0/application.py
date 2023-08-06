# -*- coding: utf-8 -*-
import json
import collections
from ..utils.http_utils import http_request
from ..utils.common_utils import print_table, obj_replace_time_field

status_summary_conf = {"successfully_deployed": u"已部署",
                       "failed_deployed": u"部署失败",
                       "executing": u"执行中",
                       "setting": u"配置中"}
source_conf = {"du": u"普通应用",
               "saas": u"SaaS应用"}


class Application(object):

    @staticmethod
    def list(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/misc/v1/applications")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"应用名称"
            header["status_summary"] = u"当前状态"
            header["cpu_limit"] = u"CPU(核)"
            header["memory_limit"] = u"内存(M)"
            header["service_num"] = u"服务数"
            header["service_running_num"] = u"运行中服务"
            header["task_num"] = u"任务数"
            header["task_running_num"] = u"运行中任务"
            header["source"] = u"来源"
            header["creater"] = u"创建人"
            header["create_time"] = u"创建时间"
            applications_info = []
            applications = data.get("applications", [])
            users = data.get("users", {})
            for application in applications:
                application = obj_replace_time_field(application, ["create_time"])
                application["status_summary"] = status_summary_conf.get(application.get("status_summary", ""), u"")
                application["source"] = source_conf.get(application.get("source", ""), u"")
                application_info = [application.get(key, "") for key in header]
                creater_name = users.get(application.get("creater", ""), {}).get("nickname", "") \
                               or users.get(application.get("creater", ""), {}).get("username", "")
                application_info[header.keys().index("creater")] = creater_name
                applications_info.append(application_info)
            print_table(header.values(), applications_info)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, appid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/applications", appid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"应用名称"
            header["status_summary"] = u"当前状态"
            header["cpu_limit"] = u"CPU(核)"
            header["memory_limit"] = u"内存(M)"
            header["source"] = u"来源"
            header["create_time"] = u"创建时间"
            applications_info = []
            application = data
            application = obj_replace_time_field(application, ["create_time"])
            application["status_summary"] = status_summary_conf.get(application.get("status_summary", ""), u"")
            application["source"] = source_conf.get(application.get("source", ""), u"")
            application_info = [application.get(key, "") for key in header]
            applications_info.append(application_info)
            print_table(header.values(), applications_info)
        except Exception as e:
            raise

    @staticmethod
    def list_by_clusterid(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?cluster_id={}".format(security, address, "/dispatch/platform/v1/applications", clusterid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"应用名称"
            header["status_summary"] = u"当前状态"
            header["service_num"] = u"服务（个）"
            header["task_num"] = u"任务（个）"
            header["cpu_allocated"] = u"分配CPU（核）"
            header["cpu_limit"] = u"总CPU（核）"
            header["memory_allocated"] = u"分配内存（M）"
            header["memory_limit"] = u"总内存（M）"
            header["source"] = u"来源"
            header["create_time"] = u"创建时间"
            applications_info = []
            applications = data.get("applications", [])
            for application in applications:
                application = obj_replace_time_field(application, ["create_time"])
                application["status_summary"] = status_summary_conf.get(application.get("status_summary", ""), u"")
                application["source"] = source_conf.get(application.get("source", ""), u"")
                application_info = [application.get(key, "") for key in header]
                applications_info.append(application_info)
            print_table(header.values(), applications_info)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/application_statistics")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print u"应用状态："
            header1 = collections.OrderedDict()
            header1["du"] = u"普通应用"
            header1["saas"] = u"SaaS应用"
            header1["error"] = u"异常"
            header1["running"] = u"运行中"
            header1["setting"] = u"配置中"
            header1["total"] = u"总数"
            counts_info = []
            count = data.get("count", {})
            count_info = [count.get(key, "") for key in header1]
            counts_info.append(count_info)
            print_table(header1.values(), counts_info)
            print u"各应用CPU使用情况(核)："
            header2 = collections.OrderedDict()
            header2["id"] = u"ID"
            header2["name"] = u"应用名称"
            header2["cpu_allocated"] = u"CPU已分配"
            header2["cpu_total"] = u"CPU总数"
            cpus_info = []
            cpus = data.get("ranks", {}).get("cpu", [])
            for cpu in cpus:
                cpu.update(cpu.get("resource_info", {}))
                cpu_info = [cpu.get(key, "") for key in header2]
                cpus_info.append(cpu_info)
            print_table(header2.values(), cpus_info)
            print u"各应用内存使用情况(M)："
            header3 = collections.OrderedDict()
            header3["id"] = u"ID"
            header3["name"] = u"应用名称"
            header3["memory_allocated"] = u"内存已分配"
            header3["memory_total"] = u"内存总数"
            memorys_info = []
            memorys = data.get("ranks", {}).get("memory", [])
            for memory in memorys:
                memory.update(memory.get("resource_info", {}))
                memory_info = [memory.get(key, "") for key in header3]
                memorys_info.append(memory_info)
            print_table(header3.values(), memorys_info)
        except Exception as e:
            raise

    @staticmethod
    def entrance_list(auth, appid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/applications", appid)
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
            header["application_id"] = u"应用ID"
            header["service_id"] = u"服务ID"
            header["name"] = u"应用入口"
            header["url"] = u"访问地址"
            entrances_info = []
            application_entrances = data.get("application_entrances", [])
            for application_entrance in application_entrances:
                entrance_info = [application_entrance.get(key, "") for key in header]
                entrances_info.append(entrance_info)
            print_table(header.values(), entrances_info)
        except Exception as e:
            raise


    @staticmethod
    def statistics_by_id(auth, appid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?type=application&ids={}".format(security, address, "/dispatch/platform/v1/statistics", appid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print u"资源状态："
            header1 = collections.OrderedDict()
            header1["application_id"] = u"ID"
            header1["cpu_allocated"] = u"CPU已分配（核）"
            header1["cpu_total"] = u"CPU总数"
            header1["memory_allocated"] = u"内存已分配（M）"
            header1["memory_total"] = u"内存总量"
            resources_info = []
            apps = data
            for app in apps:
                app.update(app.get("resources", {}))
                resource_info = [app.get(key, "") for key in header1]
                resources_info.append(resource_info)
            print_table(header1.values(), resources_info)
            print u"服务运行情况："
            header2 = collections.OrderedDict()
            header2["running"] = u"已上线"
            header2["setting"] = u"配置中"
            header2["total"] = u"总数"
            services_info = []
            for app in apps:
                app.update(app.get("services", {}))
                service_info = [app.get(key, "") for key in header2]
                services_info.append(service_info)
            print_table(header2.values(), services_info)
            print u"任务运行情况："
            header3 = collections.OrderedDict()
            header3["running"] = u"已上线"
            header3["setting"] = u"配置中"
            header3["total"] = u"总数"
            tasks_info = []
            for app in apps:
                app.update(app.get("tasks", {}))
                task_info = [app.get(key, "") for key in header3]
                tasks_info.append(task_info)
            print_table(header3.values(), tasks_info)
        except Exception as e:
            raise

    @staticmethod
    def delete(auth, appid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/applications", appid)
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        response_data = json.dumps(dict())
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=response_data, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"删除应用 {} 成功".format(appid))
        except Exception as e:
            raise

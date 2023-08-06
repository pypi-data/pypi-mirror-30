# -*- coding: utf-8 -*-
import json
import sys
import collections
from ..utils.http_utils import http_request
from ..utils.common_utils import print_table, obj_replace_time_field

lifecycle_conf = {"running": u"已上线",
                  "setting": u"未上线",
                  "executing": u"上线中"}


class Cluster(object):
    @staticmethod
    def list(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/misc/v1/clusters")
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
            header["name"] = u"集群名称"
            header["lifecycle"] = u"当前状态"
            header["application_num"] = u"应用数"
            header["creater"] = u"创建人"
            header["create_time"] = u"创建时间"
            clusters_info = []
            clusters = data.get("clusters", [])
            users = data.get("users", {})
            for cluster in clusters:
                cluster = obj_replace_time_field(cluster, ["create_time"])
                cluster["lifecycle"] = lifecycle_conf.get(cluster.get("lifecycle", ""), u"")
                cluster_info = [cluster.get(key, "") for key in header]
                creater_name = users.get(cluster.get("creater", ""), {}).get("nickname", "") \
                               or users.get(cluster.get("creater", ""), {}).get("username", "")
                cluster_info[header.keys().index("creater")] = creater_name
                clusters_info.append(cluster_info)
            print_table(header.values(), clusters_info)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        try:
            url = "{}://{}{}?ids={}".format(security, address, "/dispatch/platform/v1/clusters", clusterid)
            http_method = "GET"
            headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"集群名称"
            header["lifecycle"] = u"当前状态"
            header["create_time"] = u"创建时间"
            clusters_info = []
            clusters = data.get("clusters", [])
            for cluster in clusters:
                cluster = obj_replace_time_field(cluster, ["create_time"])
                cluster["lifecycle"] = lifecycle_conf.get(cluster.get("lifecycle", ""), u"")
                cluster_info = [cluster.get(key, "") for key in header]
                clusters_info.append(cluster_info)
            print_table(header.values(), clusters_info)
        except Exception as e:
            raise

    @staticmethod
    def statistics_by_id(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url1 = "{}://{}{}?type=cluster&ids={}".format(security, address, "/dispatch/platform/v1/statistics", clusterid)
        url2 = "{}://{}{}/{}".format(security, address, "/dispatch/nodemonitor/v1/clusters", clusterid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url1, http_method=http_method, headers=headers)
            data1 = json.loads(response_data)
            if status != 200:
                message = data1.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            status, response_data = http_request(url=url2, http_method=http_method, headers=headers)
            data2 = json.loads(response_data)
            if status != 200:
                message = data2.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            header = collections.OrderedDict()
            header["cluster_id"] = "ID"
            header["cluster_name"] = u"集群名称"
            header["total"] = u"主机总数（个）"
            header["running"] = u"已上线"
            header["executing"] = u"上线中"
            header["setting"] = u"配置中"
            header["cpu_total"] = u"CPU总数（个）"
            header["cpu_used"] = u"CPU已使用"
            header["cpu_usage"] = u"CPU使用率（%）"
            header["disk_total"] = u"磁盘总数（G）"
            header["disk_used"] = u"磁盘已使用"
            header["disk_usage"] = u"磁盘使用率（%）"
            header["memory_total"] = u"内存总数（M）"
            header["memory_used"] = u"内存已使用"
            header["memory_usage"] = u"内存使用率（%）"
            clusters_info = []
            clusters = data1
            for cluster in clusters:
                nodes = cluster.get("nodes", {})
                resources = cluster.get("resources", {})
                cluster.update(nodes)
                cluster.update(resources)
                cluster.update(data2)
                cluster["cpu_used"] = int(cluster.get("cpu_used", 0))
                cluster["cpu_total"] = int(cluster.get("cpu_total", 0))
                cluster_info = [cluster.get(key, "") for key in header]
                clusters_info.append(cluster_info)
            print_table(header.values(), clusters_info)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/cluster_statistics")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print u"应用状态："
            header1 = collections.OrderedDict()
            header1["error"] = u"异常"
            header1["running"] = u"运行中"
            header1["setting"] = u"配置中"
            header1["executing"] = u"执行中"
            header1["total"] = u"总数"
            counts_info = []
            count = data.get("count", {})
            count_info = [count.get(key, "") for key in header1]
            counts_info.append(count_info)
            print_table(header1.values(), counts_info)
            print u"各集群CPU使用情况(核)："
            header2 = collections.OrderedDict()
            header2["cluster_id"] = u"ID"
            header2["cluster_name"] = u"集群名称"
            header2["cpu_used"] = u"CPU已使用"
            header2["cpu_total"] = u"CPU总数"
            cpus_info = []
            cpus = data.get("ranks", {}).get("cpu", [])
            for cpu in cpus:
                cpu["cpu_used"] = int(cpu.get("cpu_used", 0))
                cpu["cpu_total"] = int(cpu.get("cpu_total", 0))
                cpu_info = [cpu.get(key, "") for key in header2]
                cpus_info.append(cpu_info)
            print_table(header2.values(), cpus_info)
            print u"各集群内存使用情况(M)："
            header3 = collections.OrderedDict()
            header3["cluster_id"] = u"ID"
            header3["cluster_name"] = u"集群名称"
            header3["memory_used"] = u"内存已使用"
            header3["memory_total"] = u"内存总数"
            memorys_info = []
            memorys = data.get("ranks", {}).get("memory", [])
            for memory in memorys:
                memory_info = [memory.get(key, "") for key in header3]
                memorys_info.append(memory_info)
            print_table(header3.values(), memorys_info)
        except Exception as e:
            raise

    @staticmethod
    def delete(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/clusters", clusterid)
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
            print (u"删除cluster {} 成功".format(clusterid))
        except Exception as e:
            raise








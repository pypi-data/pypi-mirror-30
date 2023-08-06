# -*- coding: utf-8 -*-
import json
import collections
from ..utils.http_utils import http_request
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
occupied_conf = {True: u"已用",
                 False: u"可用"}
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


class CommonNode(object):

    @staticmethod
    def list(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/common_nodes")
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
            header["name"] = u"主机名"
            header["occupied"] = u"当前状态"
            header["ip"] = u"服务IP"
            header["administration_ip"] = u"管理IP"
            header["username"] = u"用户名"
            header["ssh_port"] = u"端口"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名称"
            header["data_dirs"] = u"数据目录"
            header["create_time"] = u"创建时间"
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                node["occupied"] = occupied_conf.get(node.get("occupied", None), u"")
                node_info = [node.get(key, "") for key in header]
                nodes_info.append(node_info)
            for node_info in nodes_info:
                data_dirs_tmp = node_info[header.keys().index("data_dirs")]
                # format
                # [{ "path": "/data","default": true,"name": "normal"},
                #  {"path": "/ssd","default": false,"name": "ssh"}]
                # to
                # "normal:/data\nssh:/ssd"
                data_dirs = "\n".join(["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs_tmp])
                node_info[header.keys().index("data_dirs")] = data_dirs
            print_table(header.values(), nodes_info)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, machineid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        machineid = [machineid]
        url = "{}://{}{}{}".format(security, address, "/dispatch/platform/v1/common_nodes?ids=", ",".join(machineid))
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
            header["name"] = u"主机名"
            header["occupied"] = u"当前状态"
            header["ip"] = u"服务IP"
            header["administration_ip"] = u"管理IP"
            header["username"] = u"用户名"
            header["ssh_port"] = u"端口"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名称"
            header["data_dirs"] = u"数据目录"
            header["create_time"] = u"创建时间"
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                node["occupied"] = occupied_conf.get(node.get("occupied", None), u"")
                node_info = [node.get(key, "") for key in header]
                nodes_info.append(node_info)
            for node_info in nodes_info:
                data_dirs_tmp = node_info[header.keys().index("data_dirs")]
                # format
                # [{ "path": "/data","default": true,"name": "normal"},
                #  {"path": "/ssd","default": false,"name": "ssh"}]
                # to
                # "normal:/data\nssh:/ssd"
                data_dirs = "\n".join(
                    ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs_tmp])
                node_info[header.keys().index("data_dirs")] = data_dirs
            print_table(header.values(), nodes_info)
        except Exception as e:
            raise

    @staticmethod
    def list_by_clusterid(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url1 = "{}://{}{}?cluster_id={}".format(security, address, "/dispatch/platform/v1/nodes", clusterid)
        url2 = "{}://{}{}?cluster_id={}".format(security, address, "/dispatch/nodemonitor/v1/nodes", clusterid)
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
            usages = {}
            for _k, _v in data2.items():
                if not isinstance(_v, list):
                    continue
                for v in _v:
                    usages.setdefault(v.get("node_id", ""), {}).setdefault(_k, v.get("value", 0))
                    # usages[v.get("node_id", "")][_k] = v.get("value", 0)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"主机名"
            header["status_summary_running"] = u"当前状态"
            header["ip"] = u"服务IP"
            header["administration_ip"] = u"管理IP"
            header["username"] = u"用户名"
            header["ssh_port"] = u"端口"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名称"
            header["data_dirs"] = u"数据目录"
            header["cpu_usages"] = u"CPU使用率（%）"
            header["disk_usages"] = u"磁盘使用率（%）"
            header["memory_usages"] = u"内存使用率（%）"
            header["create_time"] = u"创建时间"
            nodes_info = []
            nodes = data1.get("nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                status_summary_running = status_format(node.get("lifecycle", ""), lifecycle_conf,
                                                       node.get("status_summary", ""), status_summary_conf,
                                                       node.get("running_status", ""), running_status_conf)
                node["status_summary_running"] = status_summary_running
                node.update(usages.get(node.get("id", ""), {}))
                node_info = [node.get(key, "") for key in header]
                nodes_info.append(node_info)
            for node_info in nodes_info:
                data_dirs_tmp = node_info[header.keys().index("data_dirs")]
                # format
                # [{ "path": "/data","default": true,"name": "normal"},
                #  {"path": "/ssd","default": false,"name": "ssh"}]
                # to
                # "normal:/data\nssh:/ssd"
                data_dirs = "\n".join(
                    ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs_tmp])
                node_info[header.keys().index("data_dirs")] = data_dirs
            print_table(header.values(), nodes_info)
        except Exception as e:
            raise

    @staticmethod
    def statistic(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/statistics?type=common_node")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            # header = ["running", "total", "occupied", "disk", "memory", "cpu"]
            header = collections.OrderedDict()
            header["total"] = u"主机总数"
            header["occupied"] = u"已用"
            header["disk"] = u"磁盘总量(G)"
            header["memory"] = u"内存总量(M)"
            header["cpu"] = u"CPU总量(核)"
            nodes_info = []
            nodes = data.get("common_nodes", {})
            nodes.update(data.get("resources", {}))
            node_info = [nodes.get(key, "") for key in header]
            nodes_info.append(node_info)
            print_table(header.values(), nodes_info)
        except Exception as e:
            print "HOST ERROR:" + e.message

    @staticmethod
    def deploy_batch(auth, clusterid, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids,
                                       cluster_id=clusterid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"主机 {} 上线命令发送成功".format(','.join(machineids)))
        except Exception as e:
            raise

    @staticmethod
    def undeploy_batch(auth, clusterid, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids,
                                       cluster_id=clusterid,
                                       delete_data=True))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"主机 {} 下线命令发送成功".format(','.join(machineids)))
        except Exception as e:
            raise

    @staticmethod
    def delete_batch(auth, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/common_nodes")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"主机 {} 删除成功".format(','.join(machineids)))
        except Exception as e:
            raise

    @staticmethod
    def add_batch(auth, clusterid, machineids, virtual_node_num):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes")
        http_method = "POST"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(cluster_id=clusterid,
                                       common_nodes=
                                       [dict(common_node_id=machineid,
                                             virtual_node_num=virtual_node_num) for machineid in machineids]
                                       ))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"添加主机 {} 到集群 {} 成功".format(','.join(machineids), clusterid))
        except Exception as e:
            raise

    @staticmethod
    def remove_batch(auth, clusterid, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids,
                                       cluster_id=clusterid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"从集群 {} 移除主机 {} 成功".format(clusterid, ','.join(machineids)))
        except Exception as e:
            raise












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

class MicroService(object):
    @staticmethod
    def list(auth, serviceid):
        """根据服务ID显示该服务下微服务列表"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?edit_mode=false&service_id={}".format(security, address, "/dispatch/platform/v1/micro_services", serviceid)
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
            header["name"] = u"微服务名"
            header["status_summary_running"] = u"当前状态"
            header["service_id"] = u"服务ID"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["prototype"] = u"服务类型"
            header["instance_num"] = u"实例数"
            header["version"] = u"版本"
            header["cpu"] = u"CPU（核）"
            header["memory"] = u"内存（M）"
            header["create_time"] = u"创建时间"
            microservices_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                microservice = obj_replace_time_field(microservice, ["create_time"])
                status_summary_running = status_format(microservice.get("lifecycle", ""), lifecycle_conf,
                                                       microservice.get("status_summary", ""), status_summary_conf,
                                                       microservice.get("running_status", ""), running_status_conf)
                microservice["status_summary_running"] = status_summary_running
                microservice_info = [microservice.get(key, "") for key in header]
                microservices_info.append(microservice_info)
            print_table(header.values(), microservices_info)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth, serviceid):
        """根据服务ID统计该服务下微服务信息"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?edit_mode=False&service_id={}".format(security, address, "/dispatch/platform/v1/micro_services",
                                                                 serviceid)
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
            header["cpu"] = u"CPU（核）"
            header["instance_num"] = u"实例个数"
            header["memory"] = u"内存（M）"
            header["micro_service_num"] = u"微服务数"
            statistics_infos = []
            statistics = data.get("statistics", {})
            statistics_info = [statistics.get(key, "") for key in header]
            statistics_infos.append(statistics_info)
            print_table(header.values(), statistics_infos)
        except Exception as e:
            raise

    @staticmethod
    def delete_batch(auth, serviceid, microserviceids):
        """批量删除微服务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/micro_services")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=microserviceids,
                                       service_id=serviceid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"微服务 {} 删除成功".format(','.join(microserviceids)))
        except Exception as e:
            raise

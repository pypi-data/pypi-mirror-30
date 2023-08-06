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


class Service(object):
    @staticmethod
    def list(auth, appid):
        """根据应用ID显示该应用下服务列表"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?application_id={}".format(security, address, "/dispatch/platform/v1/services", appid)
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
            header["name"] = u"服务名"
            header["status_summary_running"] = u"当前状态"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名"
            header["prototype"] = u"类型"
            header["version"] = u"版本"
            header["micro_service_num"] = u"微服务数"
            header["cpu_allocated_total"] = u"CPU使用率（核）"
            header["memory_allocated_total"] = u"内存使用率（M）"
            header["create_time"] = u"创建时间"
            services_info = []
            services = data.get("services", [])
            for service in services:
                service["cpu_allocated_total"] = "{}/{}".format(
                    service.get("resource_info", {}).get("cpu_allocated", "NaN"),
                    service.get("resource_info", {}).get("cpu_total", "NaN"))
                service["memory_allocated_total"] = "{}/{}".format(
                    service.get("resource_info", {}).get("memory_allocated", "NaN"),
                    service.get("resource_info", {}).get("memory_total", "NaN"))
                service = obj_replace_time_field(service, ["create_time"])
                status_summary_running = status_format(service.get("lifecycle", ""), lifecycle_conf,
                                                       service.get("status_summary", ""), status_summary_conf,
                                                       service.get("running_status", ""), running_status_conf)
                service["status_summary_running"] = status_summary_running
                service_info = [service.get(key, "") for key in header]
                services_info.append(service_info)
            print_table(header.values(), services_info)
        except Exception as e:
            raise

    @staticmethod
    def deploy_batch(auth, appid, serviceids):
        """服务上线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"服务 {} 上线指令发送成功".format(','.join(serviceids)))
        except Exception as e:
            raise

    @staticmethod
    def undeploy_batch(auth, appid, serviceids):
        """服务下线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid,
                                       delete_data=True))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"服务 {} 下线指令发送成功".format(','.join(serviceids)))
        except Exception as e:
            raise

    @staticmethod
    def delete_batch(auth, appid, serviceids):
        """批量删除服务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"服务 {} 删除成功".format(','.join(serviceids)))
        except Exception as e:
            raise

    # @staticmethod
    # def delete(auth, serviceid):
    #     """删除服务"""
    #     print("delete service")

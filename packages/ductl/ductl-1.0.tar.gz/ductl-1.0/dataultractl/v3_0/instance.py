# -*- coding: utf-8 -*-
import json
import os
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


class Instance(object):
    @staticmethod
    def _list(auth, serviceid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?edit_mode=false&service_id={}".format(security, address, "/dispatch/platform/v1/micro_services",
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
            return data
        except Exception as e:
            raise

    @staticmethod
    def list(auth, serviceid):
        """根据服务ID显示该应用下实例列表"""
        try:
            data = Instance._list(auth, serviceid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"实例名"
            header["status_summary_running"] = u"当前状态"
            header["micro_service_id"] = u"微服务ID"
            header["service_id"] = u"服务ID"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["node_id"] = u"主机ID"
            header["node_name"] = u"主机名"
            header["data_path_instance"] = u"数据目录"
            header["create_time"] = u"创建时间"
            instances_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                for instance in microservice.get("instances", []):
                    instance["node_id"] = instance.get("node_id") or instance.get("running_node_id")
                    instance["node_name"] = instance.get("node_name") or instance.get("running_node_name")
                    status_summary_running = status_format(instance.get("lifecycle", ""), lifecycle_conf,
                                                           instance.get("status_summary", ""), status_summary_conf,
                                                           instance.get("running_status", ""), running_status_conf)
                    instance["status_summary_running"] = status_summary_running
                    instance = obj_replace_time_field(instance, ["create_time"])
                    instance_info = [instance.get(key, "") for key in header]
                    instances_info.append(instance_info)
            print_table(header.values(), instances_info)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, instanceid):
        """查询单个实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/instances", instanceid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            return data
        except Exception as e:
            raise

    @staticmethod
    def deploy_batch(auth, serviceid, microserviceid, instanceids):
        """部署实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/instances/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=instanceids,
                                       micro_service_id=microserviceid,
                                       service_id=serviceid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"实例 {} 部署指令发送成功".format(','.join(instanceids)))
        except Exception as e:
            raise

    @staticmethod
    def undeploy_batch(auth, serviceid, microserviceid, instanceids):
        """卸载实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/instances/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=instanceids,
                                       micro_service_id=microserviceid,
                                       service_id=serviceid,
                                       delete_data=False))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"实例 {} 卸载指令发送成功".format(','.join(instanceids)))
        except Exception as e:
            raise

    @staticmethod
    def delete_batch(auth, serviceid, microserviceid, instanceids):
        """批量删除实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/instances")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=instanceids,
                                       micro_service_id=microserviceid,
                                       service_id=serviceid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            print (u"实例 {} 删除成功".format(','.join(instanceids)))
        except Exception as e:
            raise

    @staticmethod
    def add_batch(auth, serviceid, microserviceid, instanceids):
        """批量添加实例"""
        print(u"功能暂未开放")

    @staticmethod
    def log(auth, instanceid):
        """实例日志"""
        short_auth_token, short_access_authority_token = auth.get_short_token()
        data = Instance.show(auth, instanceid)
        domain_name_service = data.get("domain_name_service", "")
        if not domain_name_service:
            raise Exception(u"domain name service异常")
        wsurl = "http://{}/webtty/{}:59998/{}/{}/ins_id={}".format(auth.address, domain_name_service, short_auth_token,
                                                             short_access_authority_token, instanceid)
        try:
            cmd = "{} {}".format(auth.ttyclient, wsurl)
            # print cmd
            os.system(cmd)
        except KeyboardInterrupt:
            # print u"exit"
            exit(0)
        except Exception:
            raise

    @staticmethod
    def terminal(auth, serviceid, instanceid):
        """实例终端"""
        short_auth_token, short_access_authority_token = auth.get_short_token()
        data = Instance.show(auth, instanceid)
        domain_name_service = data.get("domain_name_service", "")
        if not domain_name_service:
            raise Exception(u"domain name service异常")
        wsurl = "http://{}/webtty/{}:59999/{}/{}/ins_id={}".format(auth.address, domain_name_service, short_auth_token,
                                                                   short_access_authority_token, instanceid)
        try:
            cmd = "{} {}".format(auth.ttyclient, wsurl)
            # print cmd
            os.system(cmd)
        except KeyboardInterrupt:
            # print u"exit"
            exit(0)
        except Exception:
            raise
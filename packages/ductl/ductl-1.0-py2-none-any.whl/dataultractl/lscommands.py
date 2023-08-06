# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.cluster import Cluster
from .v3_0.commonnode import CommonNode as CN
from .v3_0.application import Application
from .v3_0.service import Service
from .v3_0.task import Task
from .v3_0.microservice import MicroService
from .v3_0.instance import Instance


class LsCommands(object):
    @args("--clusterid", dest="clusterid", default=None, help=u"根据ID显示集群信息")
    def cluster(self, auth, clusterid=None):
        """显示集群列表"""
        if clusterid:
            Cluster().show(auth, clusterid)
        else:
            Cluster().list(auth)

    @args("--machineid", dest="machineid", default=None, help=u"根据ID显示主机信息")
    @args("--clusterid", dest="clusterid", default=None, help=u"根据集群ID显示该集群下主机列表")
    def machine(self, auth, machineid=None, clusterid=None):
        """显示通用主机列表"""
        if not machineid and not clusterid:
            CN.list(auth)
        elif not clusterid:
            CN.show(auth, machineid)
        elif not machineid:
            CN.list_by_clusterid(auth, clusterid)
        else:
            raise Exception(u"参数错误")

    @args("--appid", dest="appid", default=None, help=u"根据ID显示应用信息")
    @args("--clusterid", dest="clusterid", default=None, help=u"根据集群ID显示该集群下应用信息")
    def application(self, auth, appid=None, clusterid=None):
        """显示应用列表"""
        if not appid and not clusterid:
            Application.list(auth)
        elif not clusterid:
            Application.show(auth, appid)
        elif not appid:
            Application.list_by_clusterid(auth, clusterid)
        else:
            raise Exception(u"参数错误")

    @args("--appid", dest="appid", required=True, help=u"根据应用ID显示该应用下服务列表")
    def service(self, auth, appid):
        """显示服务列表"""
        Service.list(auth, appid)

    @args("--appid", dest="appid", required=True, help=u"根据应用ID显示该应用下任务列表")
    def task(self, auth, appid):
        """显示任务列表"""
        Task.list(auth, appid)

    @args("--serviceid", dest="serviceid", required=True, help=u"根据服务ID显示该服务下微服务列表")
    def microservice(self, auth, serviceid):
        """显示微服务列表"""
        MicroService.list(auth, serviceid)

    @args("--serviceid", dest="serviceid", required=True, help=u"实例对应的服务id")
    def instance(self, auth, serviceid):
        """显示实例列表"""
        Instance.list(auth, serviceid)

    # @args("--serviceid", dest="serviceid", required=True, help=u"实例对应的服务id")
    # @args("--instanceid", dest="instanceid", help=u"实例id")
    # @args("-t", dest="terminal_flag", default=False, action='store_true', help=u"开启终端,必须输入instanceid及serviceid")
    # @args("-l", dest="log_flag", default=False, action='store_true', help=u"查看日志,必须输入instanceid及serviceid")
    # def instance(self, auth, serviceid, instanceid, terminal_flag, log_flag):
    #     """显示实例列表"""
    #     if terminal_flag and log_flag:
    #         raise Exception(u"参数错误")
    #     elif not terminal_flag and not log_flag:
    #         Instance.list(auth, serviceid)
    #     elif not log_flag:
    #         Instance.terminal(auth, serviceid, instanceid)
    #     else:
    #         Instance.log(auth, serviceid, instanceid)


    # @args("--serviceid", dest="serviceid", required=True, help=u"根据服务id查询实例")
    # @args("--instanceid", dest="instanceid", required=True, help=u"根据实例id查询log")
    # def instance_log(self, auth, servieid, instanceid):
    #     """显示实例日志"""
    #     Instance.log(auth, servieid, instanceid)
    #
    # @args("--serviceid", dest="serviceid", required=True, help=u"根据服务id查询实例")
    # @args("--instanceid", dest="instanceid", required=True, help=u"根据实例id查询log")
    # def instance_terminal(self, auth, servieid, instanceid):
    #     """显示实例日志"""
    #     Instance.terminal(auth, servieid, instanceid)
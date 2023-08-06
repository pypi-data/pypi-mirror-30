# -*- coding: utf-8 -*-
from ..utils.http_utils import http_request
from ..utils.env_utils import get_ttyclient_uri
from ..utils.common_utils import extract
import json
import ConfigParser
import os
import sys
import requests


class HttpClient(object):

    def __init__(self, loginfile=".dataultra-auth"):
        if sys.platform == "linux2":
            self.os_verify = "/etc/dataultractl/os-verify"
            self.login_conf = os.path.join(os.environ['HOME'], loginfile)
            self.ttyclient = os.path.dirname(os.path.realpath(__file__)) + "/../bin/" + "ttyclient-linux"
            self.tarpath = os.path.dirname(os.path.realpath(__file__)) + "/../"
        elif sys.platform == "win32":
            self.os_verify = "C:\\\\dataultractl\\os-verify"
            self.login_conf = loginfile
            self.ttyclient = os.path.dirname(os.path.realpath(__file__)) + "\\..\\bin\\" + "ttyclient-win.exe"
            self.tarpath = os.path.dirname(os.path.realpath(__file__)) + "\\..\\"
        else:
            raise Exception(u"不支持该操作系统")
        self.ttyclient_check()
        self.auth_token = None
        self.access_authority_token = None
        self.address = None
        self.security = None

    def get_token(self):
        try:
            # 生成config对象
            conf = ConfigParser.ConfigParser()
            # 用config对象读取配置文件
            conf.read(self.login_conf)
            if not conf.has_section("tokens"):
                raise Exception(u"请先登录")
            self.auth_token = conf.get("tokens", "auth_token")
            self.access_authority_token = conf.get("tokens", "access_authority_token")
            self.address = conf.get("tokens", "address")
            self.security = conf.get("tokens", "security")
        except Exception as e:
            raise Exception(u"口令失效，请重新登录")

    def login(self, verify_conf=None):
        if verify_conf:
            username = verify_conf.get("username")
            password = verify_conf.get("password")
            domain = verify_conf.get("domain")
            address = verify_conf.get("address")
            security = verify_conf.get("security")
        else:
            username, password, domain, address, security = self.get_verify_info()
        if address.startswith("http"):
            url = "{}{}".format(address, "/dispatch/login/v1/login")
            security = address.split("://")[0]
            address = address.split("://")[-1]
        else:
            url = "{}://{}{}".format(security, address, "/dispatch/login/v1/login")
        http_method = "POST"
        request_body = json.dumps(dict(username=username,
                            password=password,
                            domain=domain))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body,
                                                            headers={"Content-Type": "application/json"})
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            # 生成config对象
            conf = ConfigParser.ConfigParser()
            # 用config对象读取配置文件
            conf.read(self.login_conf)
            if not conf.has_section("tokens"):
                # 增加新的section
                conf.add_section('tokens')
            conf.set('tokens', 'auth_token', data.get("auth_token"))
            conf.set('tokens', 'access_authority_token', data.get("access_authority_token"))
            conf.set('tokens', 'address', address)
            conf.set('tokens', 'security', security)
            with open(self.login_conf, 'w') as fw:  # 循环写入
                conf.write(fw)
            print u"用户:{} 登录成功".format(username)
        except Exception as e:
            raise

    def logout(self):
        # 生成config对象
        conf = ConfigParser.ConfigParser()
        # 用config对象读取配置文件
        conf.read(self.login_conf)
        if not conf.has_section("tokens"):
            # 增加新的section
            conf.add_section('tokens')
        conf.remove_option('tokens', 'auth_token')
        conf.remove_option('tokens', 'access_authority_token')
        conf.remove_option('tokens', 'address')
        conf.remove_option('tokens', 'security')
        with open(self.login_conf, 'w') as fw:  # 循环写入
            conf.write(fw)
        print u"已注销"

    def get_short_token(self):
        auth_token = self.auth_token or ''
        access_authority_token = self.access_authority_token or ''
        address = self.address or ''
        security = self.security or ''
        url = "{}://{}{}".format(security, address, "/dispatch/authority/v1/shortToken")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", u"用户名或者密码错误！")
                raise Exception(message)
            return data.get("auth_token"), data.get("access_authority_token")
        except Exception as e:
            raise

    def get_verify_info(self):
        try:
            # 生成config对象
            conf = ConfigParser.ConfigParser()
            # 用config对象读取配置文件
            conf.read(self.os_verify)
            username = conf.get("verify", "username")
            password = conf.get("verify", "password")
            domain = conf.get("verify", "domain")
            address = conf.get("verify", "address")
            security = conf.get("verify", "security")
            return username, password, domain, address, security
        except Exception as e:
            raise Exception(u"请先登录")

    def ttyclient_check(self):
        if not os.path.isfile(self.ttyclient):
            print u"Downloading ttyclient......"
            download_uri = get_ttyclient_uri()
            file_name = os.path.basename(download_uri)
            r = requests.get(download_uri)
            with open(self.tarpath+file_name, "wb") as code:
                code.write(r.content)
            extract(self.tarpath+file_name, self.tarpath)
            print u"ttyclient downloaded"
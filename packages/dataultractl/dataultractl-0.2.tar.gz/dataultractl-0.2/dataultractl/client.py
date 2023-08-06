# -*- coding: utf-8 -*-
import argparse
import collections
from .statiscommands import StatisCommands
from .lscommands import LsCommands
from .addcommands import AddCommands
from .deletecommands import DeleteCommands
from .deploycommands import DeployCommands
from .undeploycommands import UndeployCommands
from .removecommands import RemoveCommands
from .startcommands import StartCommands
from .stopcommands import StopCommands
from .utils.parse_utils import args, methods_of, fetch_func_args
from .v3_0.httpclient import HttpClient
from .v3_0.instance import Instance


@args('-u', '--username', dest='username', help='use for auth')
@args('-p', '--password', dest='password', help='use for auth')
@args('-d', '--domain', dest='domain', type=str, choices=['huayun.com', 'bigdata.com'], help='use for auth')
@args('-a', '--address', dest='address', type=str, help='dataultra address')
@args('-s', '--security', dest='security', type=str, default='http', choices=['http', 'https'], help='protocol of dataultra address')
def login(username, password, domain, address, security):
    """login   [[-u|--username USERNAME]
                [-p|--password PASSWORD]
                [-d|--domain DOMAIN]
                [-a|--address ADDRESS]
                [-s|--security SECURITY(http,https)]| ]"""
    if username and password and domain and address:
        verify_conf = {"username": username,
                       "password": password,
                       "domain": domain,
                       "address": address,
                       "security": security}
        httpclient = HttpClient()
        httpclient.login(verify_conf)
    elif not (username or password or domain or address):
        httpclient = HttpClient()
        httpclient.login()
    else:
        raise Exception(u"参数错误")


def logout():
    """logout"""
    httpclient = HttpClient()
    httpclient.logout()


@args('instanceid', help='instance id')
def _log(auth, instanceid):
    """show log of instance"""
    Instance.log(auth, instanceid)


@args('instanceid', help='instance id')
def _exec(auth, instanceid):
    """execute command on the terminal of instance"""
    Instance.terminal(auth, instanceid)


class Client(object):
    CATEGORIES_FUNC = {
        'login': login,
        'logout': logout,
        'log': _log,
        'exec': _exec
    }
    CATEGORIES = collections.OrderedDict()
    CATEGORIES["ls"] = (LsCommands, "list cluster|machine|application|service|task|microservice|instance info")
    CATEGORIES["statistics"] = (StatisCommands, "statistic cluster|machine|application|microservice")
    CATEGORIES["deploy"] = (DeployCommands, "deploy machine|service|instance|task")
    CATEGORIES["undeploy"] = (UndeployCommands, "undeploy machine|service|instance|task")
    CATEGORIES["delete"] = (DeleteCommands, "delete cluster|machine|application|service|task|microservice|instance")
    CATEGORIES["add"] = (AddCommands, "add  machine|instance")
    CATEGORIES["remove"] = (RemoveCommands, "remove machine")
    CATEGORIES["start"] = (StartCommands, "start task")
    CATEGORIES["stop"] = (StopCommands, "stop task")

    def get_base_parser(self):
        parser = argparse.ArgumentParser(prog="ductl")
        return parser

    def get_subcommand_parser(self):
        top_parser = self.get_base_parser()
        subparsers = top_parser.add_subparsers()

        for category_func in self.CATEGORIES_FUNC:
            func = self.CATEGORIES_FUNC[category_func]
            command_object = func
            category_func_parser = subparsers.add_parser(category_func, help=command_object.__doc__)

            action_kwargs = []
            for args, kwargs in getattr(command_object, 'args', []):
                category_func_parser.add_argument(*args, **kwargs)
            category_func_parser.set_defaults(action_fn=command_object)
            category_func_parser.set_defaults(action_kwargs=action_kwargs)

        for category in self.CATEGORIES:
            cls, help_mes = self.CATEGORIES[category]
            command_object = cls()

            category_parser = subparsers.add_parser(category, help=help_mes)
            category_parser.set_defaults(command_object=command_object)

            category_subparsers = category_parser.add_subparsers(dest='action')
            for (action, action_fn, action_help) in methods_of(command_object):
                parser = category_subparsers.add_parser(action, help=action_help)

                action_kwargs = []
                for args, kwargs in getattr(action_fn, 'args', []):
                    parser.add_argument(*args, **kwargs)

                parser.set_defaults(action_fn=action_fn)
                parser.set_defaults(action_kwargs=action_kwargs)
        return top_parser

    def main(self, argv):
        parser = self.get_subcommand_parser()
        args = parser.parse_args(argv)

        try:
            # print 'match_args:', args
            fn = getattr(args, "action_fn", None)
            if fn:
                fn_args = fetch_func_args(fn, args)
                if fn.func_name != "login" and fn.func_name != "logout":
                    authclient = HttpClient()
                    authclient.get_token()
                    # do the match func
                    fn(authclient, *fn_args)
                else:
                    # do the match func
                    fn(*fn_args)
            else:
                parser.print_help()
        except Exception as e:
            # parser.print_help()
            raise

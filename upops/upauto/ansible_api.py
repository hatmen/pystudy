# -*- coding:utf-8 -*-

from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.inventory import Inventory
from ansible.runner import Runner
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils
import logging
import os

API_DIR = os.path.dirname(os.path.abspath(__file__))
ANSIBLE_DIR = os.path.join(API_DIR, 'playbooks')

logging.basicConfig()
loginfo = logging.getLogger('upops_info')
logerror = logging.getLogger(('upops_error'))


class AnsibleError(StandardError):
    def __init__(self, error, data='', message=''):
        super(AnsibleError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class CommandValueError(AnsibleError):
    def __init__(self, field, message=''):
        super(CommandValueError, self).__init__('value:invalid', field, message)


class MyInventory(Inventory):
    def __init__(self, resource):
        """
        resource的数据格式是一个列表字典，比如
            {
                "group1": {
                    "hosts": [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...],
                    "vars": {"var1": value1, "var2": value2, ...}
                }
            }

        如果你只传入1个列表，这默认该列表内的所有主机属于my_group组,比如
            [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...]
        """
        self.resource = resource
        self.inventory = Inventory(host_list=[])
        self.gen_inventory()
        
    def my_add_group(self, hosts, groupname, groupvars=None):
        my_group = Group(name=groupname)
        if groupvars:
            for key, value in groupvars.iteritems():
                my_group.set_variable(key, value)

        for host in hosts:
            hostname = host.get('hostname')
            hostip = host.get('ip', hostname)
            hostport = host.get('port', 22)
            username = host.get('username', 'root')
            password = host.get('password')
            ssh_key = host.get("ssh_key")
            my_host = Host(name=hostname, port=hostport)
            my_host.set_variable('ansible_ssh_host', hostip)
            my_host.set_variable('ansible_ssh_port', hostport)
            my_host.set_variable('ansible_ssh_user', username)
            my_host.set_variable('ansible_ssh_pass', password)
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)

            for key, value in host.iteritems():
                if key not in ['hostname', 'port', 'username', 'password']:
                    my_host.set_variable(key, value)
            my_group.add_host(my_host)
        self.inventory.add_group(my_group)
        

    def gen_inventory(self):
        if isinstance(self.resource, list):
            self.my_add_group(self.resource, 'default_group')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.iteritems():
                self.my_add_group(hosts_and_vars.get('hosts'), groupname, hosts_and_vars.get('vars'))


class MyRunner(MyInventory):
    def __init__(self, *args, **kwargs):
        super(MyRunner, self).__init__(*args, **kwargs)
        self.results_raw = {}

    def run(self, module_name='shell', module_args='', timeout=10, forks=10, pattern='*', become=False, become_method='sudo', become_user='root', become_pass=''):
        hoc = Runner(module_name=module_name,
                     module_args=module_args,
                     timeout=timeout,
                     inventory=self.inventory,
                     pattern=pattern,
                     forks=forks,
                     become=become,
                     become_user=become_user,
                     become_method=become_method,
                     become_pass=become_pass
                     )
        self.result_raw = hoc.run()
        loginfo.info(self.result_raw)
        return self.result_raw
    
    @property
    def results(self):
        result = {'failed': {}, 'ok': {}}
        dark = self.result_raw.get('dark')
        contacted = self.result_raw.get('contacted')
        if dark:
            for host, info in dark.items():
                result['failed'][host] = info.get('msg')
        
        if contacted:
            for host, info in contacted.items():
                if info.get('invocation').get('module_name') in ['raw', 'shell', 'command', 'script']:
                    if info.get('rc') == 0:
                        result['ok'][host] = info.get('stdout') + info.get('stderr')
                    else:
                        result['failed'][host] = info.get('stdout') + info.get('stderr')
                else:
                    if info.get('failed'):
                        result['failed'][host] = info.get('msg')
                    else:
                        result['ok'][host] = info.get('changed')
        return result


class Command(MyInventory):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.results_raw = {}
   
    def run(self, command, module_name='command', timeout=10, forks=10, pattern='*'):
        data = {}
        if module_name not in ['raw', 'command', 'shell']:
            raise CommandValueError('module_name', "module_name must be of the 'raw, command, shell'")
        try:
            hoc = Runner(module_name=module_name,
                     module_args=command,
                     timeout=timeout,
                     inventory=self.inventory,
                     pattern=pattern,
                     forks=forks,
                     )
        except Exception, e:
            logerror.error(e)

        self.results_raw = hoc.run()
        return self.results_raw

    @property
    def results(self):
        result = {}
        for k, v in self.results_raw.items():
            if k == 'dark':
                for host, info in v.items():
                    result[host] = {'dark': info.get('msg')}
            elif k == 'contacted':
                for host, info in v.items():
                    result[host] = {}
                    if info.get('stdout'):
                        result[host]['stdout'] = info.get('stdout')
                    elif info.get('stderr'):
                        result[host]['stderr'] = info.get('stderr')
        return result

    @property
    def state(self):
        result = {}
        if self.stdout:
            result['ok'] = self.stdout
        if self.stderr:
            result['err'] = self.stderr
        if self.dark:
            result['dark'] = self.dark
        return result

    @property
    def exec_time(self):
        result = {}
        all = self.results_raw.get('contacted')
        for key ,value in all.iteritems():
            result[key] = {
                'start': value.get('start'),
                'end': value.get('end'),
                'delta': value.get('delta'), }
        return result

    @property
    def stdout(self):
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            result[key] = value.get('stdout')
        return result

    @property
    def stderr(self):
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            if value.get("stderr") or value.get("warnings"):
                result[key] = {
                    "stderr": value.get("stderr"),
                    "warnings": value.get("warnings"),}
        return result
   
    @property
    def dark(self):
        """
        get the dark results.
        """
        return self.results_raw.get("dark")


class CustomAggregateStats(callbacks.AggregateStats):
    """
    Holds stats about per-host activity during playbook runs.
    """
    def __init__(self):
        super(CustomAggregateStats, self).__init__()
        self.results = []

    def compute(self, runner_results, setup=False, poll=False,
                ignore_errors=False):
        """
        Walk through all results and increment stats.
        """
        super(CustomAggregateStats, self).compute(runner_results, setup, poll,
                                              ignore_errors)

        self.results.append(runner_results)

    def summarize(self, host):
        """
        Return information about a particular host
        """
        summarized_info = super(CustomAggregateStats, self).summarize(host)

        # Adding the info I need
        summarized_info['result'] = self.results

        return summarized_info


class MyPlaybook(MyInventory):
    """
    this is my playbook object for execute playbook.
    """
    def __init__(self, *args, **kwargs):
        super(MyPlaybook, self).__init__(*args, **kwargs)

    def run(self, playbook_relational_path, extra_vars=None):
        """
        run ansible playbook,
        only surport relational path.
        """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        playbook_path = os.path.join(ANSIBLE_DIR, playbook_relational_path)

        pb = PlayBook(
            playbook=playbook_path,
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            inventory=self.inventory,
            extra_vars=extra_vars,
            check=False)

        self.results = pb.run()

    @property
    def raw_results(self):
        """
        get the raw results after playbook run.
        """
        return self.results


class PushKey(MyRunner):
    def __init__(self, *args, **kwargs):
        super(PushKey, self).__init__(*args, **kwargs)

    def push_key(self, user, key_path):
        module_args = 'user=%s key="{{ lookup("file", "%s") }}" state=present' % (user, key_path)
        self.run("authorized_key", module_args, become=True)
        return self.results

    def del_key(self, user, key_path):
        module_args = 'user="%s" key="{{ lookup("file", "%s") }}" state="absent"' % (user, key_path)
        self.run("authorized_key", module_args, become=True)
        return self.results


if __name__ == "__main__":
    resource = [{"hostname": "192.168.1.111", "port": "22", "username": "root", "password": "czyb123"}]
    copy_key = PushKey(resource)
    #print copy_key.del_key('root', '/root/.ssh/id_rsa.pub')
    print copy_key.push_key('root', '/root/.ssh/id_rsa.pub')
    

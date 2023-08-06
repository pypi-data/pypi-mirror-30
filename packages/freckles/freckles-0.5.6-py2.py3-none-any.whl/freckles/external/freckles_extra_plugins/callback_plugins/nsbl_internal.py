from __future__ import absolute_import, division, print_function

import json
import copy
import yaml

from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
from six import string_types

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()

__metaclass__ = type


class CallbackModule(CallbackBase):
    """
    Forward task, play and result objects to freckles.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'freckles_callback'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.task = None
        self.play = None
        self.task_serialized = False
        self.play_serialized = False

    def find_role_params(self, role):

        if not role._role_params:
            parents = role._parents
            for p in parents:
                params = self.find_role_params(p)
                if params:
                    return params

        else:
            return role._role_params

        return {}
        # display.display(str(self.task._role._parents))
        # return {}


    def get_task_serialized(self):

        if not self.task_serialized:

            name = self.task.name

            if not self.task._role:
                role_params = {}
            else:
                role_params = self.find_role_params(self.task._role)

            action = self.task.action

            ignore_errors = self.task.ignore_errors
            if ignore_errors == None:
                ignore_errors = False

            self.task_serialized = task_dict = {}
            task_dict["name"] = name
            task_dict["ignore_errors"] = ignore_errors
            task_dict["action"] = action
            task_dict["role_params"] = role_params
            # self.task_serialized = self.task.serialize()


        return self.task_serialized

    def get_play_serialized(self):

        if not self.play_serialized:
            self.play_serialized = self.play.serialize()

        return self.play_serialized

    def get_task_detail(self, detail_key):

        if not self.task:
            return None

        return self.get_task_serialized().get(detail_key, None)

        # temp = self.get_task_serialized()
        # for level in detail_key.split("."):
            # temp = temp.get(level, {})

        # return temp

    def get_task_name(self):

        name = self.get_task_detail("name")
        return name

    def get_recursive_role_detail(self, detail_key, role):

        if detail_key in role.get("_role_params", {}).keys():
            return role["_role_params"][detail_key]

        for r in role.get("_parents", []):
            key = self.get_recursive_role_detail(detail_key, r)
            if isinstance(key, int):
                return key

        return None

    def get_env_id(self):

        # pprint.pprint(self.task.serialize())
        # pprint.pprint(self.play.serialize())

        task_role_params = self.get_task_detail("role_params")
        id = task_role_params.get("_env_id", None)

        return id
        # id = self.get_task_detail("role._role_params._env_id")

        # if not isinstance(id, int):
            # id = self.get_recursive_role_detail("_env_id", self.get_task_serialized().get("role", {}))

        # if isinstance(id, int):
            # return id
        # else:
            # return None

    def get_role_id(self):

        # pprint.pprint(self.task.serialize())
        # pprint.pprint(self.play.serialize())

        task_role_params = self.get_task_detail("role_params")
        id = task_role_params.get("_role_id", None)
        return id
        # id = self.get_task_detail("role._role_params._role_id")

        # if not isinstance(id, int):
            # id = self.get_recursive_role_detail("_role_id", self.get_task_serialized().get("role", {}))
        # if isinstance(id, int):
            # return id
        # else:
            # return None

            # parents = self.get_task_detail("role._parents")
            # if  parents:
            # for p in parents:
            # if "freck_id" in p["_role_params"].keys():

            # return p["_role_params"]["freck_id"]


    def print_output(self, category, result, item=None):

        # if self.task:
        # pprint.pprint(self.task.serialize())
        output = {}
        output["category"] = category

        if category == "play_start":
            roles = self.get_play_serialized().get("roles", {})
            env_id = None
            if roles and len(roles) >= 1:
                env_id = roles[0].get("_role_params", {}).get("_env_id", None)

            output["_env_id"] = env_id
            display.display(json.dumps(output, encoding='utf-8'))
            return

        if category == "failed":
            output['reason'] = result._result.get("reason", "n/a")
        temp = self.get_role_id()
        # display.display(json.dumps(output, encoding='utf-8'))
        # return
        output["_role_id"] = temp
        temp = self.get_env_id()
        output["_env_id"] = temp

        temp = self.get_task_name()
        if isinstance(temp, string_types) and temp.startswith("dyn_role"):
            task_id, task_name = temp.split(" -- ")
            output["dyn_task"] = True
            output["_dyn_task_id"] = task_id
            output["name"] = task_name
        else:
            output["dyn_task"] = False
            output["_dyn_task_id"] = None
            output["name"] = temp

        if item:
            output["item"] = item

        action = self.get_task_detail("action")
        if not action:
            action = "n/a"
        output["action"] = action

        output["ignore_errors"] = self.get_task_detail("ignore_errors")

        # output["task"] = self.task.serialize()
        # output["play"] = self.play.serialize()
        if category == "play_start" or category == "task_start":
            output["result"] = {}
        else:
            # output["result"] = result._result
            module_stderr = result._result.get("module_stderr")
            if module_stderr:
                output.setdefault("stderr", "")
                output["stderr"] = output["stderr"] + "\n{}".format(module_stderr)
                output.setdefault("stderr_lines", [])
                output["stderr_lines"].append(module_stderr)
            module_stdout = result._result.get("module_stdout")
            if module_stdout:
                output.setdefault("stdout", "")
                output["stdout"] = output["stdout"] + "\n{}".format(module_stdout)
                output.setdefault("stdout_lines", [])
                output["stdout_lines"].append(module_stdout)
            msg = result._result.get("msg", None)
            if msg:
                if msg != "MODULE FAILURE":
                    output["msg"] = msg
                else:
                    output["msg"] = module_stderr

            if not output.get("msg", False) and output.get("reason", False):
                output["msg"] = output.get("reason")

            stdout = result._result.get("stdout", None)
            if stdout:
                output["stdout"] = stdout
                output["stdout_lines"] = result._result.get("stdout_lines")
            stderr = result._result.get("stderr", None)
            if stderr:
                output["stderr"] = stderr
                output["stderr_lines"] = result._result.get("stderr_lines")

            if result._result.get('changed', False):
                status = 'changed'
            else:
                status = 'ok'
            output["status"] = status

            skipped = result._result.get('skipped', False)
            output["skipped"] = skipped

            if action == "debug":
                if result and result._result:
                    # import pprint
                    # pprint.pprint(self.get_task_serialized())
                    keys_to_remove = [k for k in result._result.keys() if k.startswith("_ansible")]
                    keys_to_remove.extend(["changed", "skipped"])

                    for key in keys_to_remove:
                        result._result.pop(key, None)

                    if len(result._result) != 1:
                        output["debug_key"] = "n/a"
                        output["debug_value"] = "Can't be determined, multiple keys: {}".format(result._result.keys())

                    output["debug_key"] = result._result.keys()[0]
                    output["debug_value"] = result._result[output["debug_key"]]


        display.display(json.dumps(output, encoding='utf-8'))

    def v2_runner_on_ok(self, result, **kwargs):

        self.print_output("ok", result)

    def v2_runner_on_failed(self, result, **kwargs):

        self.print_output("failed", result)

    def v2_runner_on_unreachable(self, result, **kwargs):

        self.print_output("unreachable", result)

    def v2_runner_on_skipped(self, result, **kwargs):

        self.print_output("skipped", result)

    def v2_playbook_on_play_start(self, play):
        self.play = play
        self.play_serialized = False
        self.print_output("play_start", None)

    def v2_playbook_on_task_start(self, task, is_conditional):

        self.task = task
        self.task_serialized = False
        self.print_output("task_start", None)

    def v2_runner_item_on_ok(self, result):

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        if isinstance(result._task, TaskInclude):
            return
        elif result._result.get('changed', False):
            status = 'changed'
        else:
            status = 'ok'

        item = self._get_item(result._result)

        self.print_output("item_ok", result, item)

    def v2_runner_item_on_failed(self, result):
        item = self._get_item(result._result)
        self.print_output("item_failed", result, item)

    def v2_runner_item_on_skipped(self, result):
        item = self._get_item(result._result)
        self.print_output("item_skipped", result, item)

    def v2_on_any(self, *args, **kwargs):

        # pprint.pprint(args)
        pass

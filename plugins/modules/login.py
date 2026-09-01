#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import hashlib
import urllib

import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: login

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: creates authenticated session, to be used by further modules

description:
    - For API access a valid session is required.
    - This module executes a login and exposes session_id for other modules to be used

options:
    host:
        description:
            - host (-address) of LPOS API endpoint
        required: true
        type: str
    port:
        description:
            - host-port of LPOS API endpoint
        required: false
        type: int
        default: 80
    path:
        description:
            - base-path for LPOS API
        required: false
        type: str
        default: /api/
    user:
        description:
            - user (name) to authenticate on LPOS instance
        required: true
        type: str
    password:
        description:
            - password to authenticate on LPOS instance
        required: true
        type: str
"""

EXAMPLES = r"""
# execute login
- name: execute LPOS API login
  nils_ost.lpos.login:
    host: "{{ ansible_host }}"
    user: "{{ root_login }}"
    password: "{{ root_password }}"
  delegate_to: localhost
  register: lpos
"""

RETURN = r"""
url:
    description:
        - the URL build from host, port and path, to be used on other modules
    type: str
    returned: always
    sample: 'http://192.168.0.5:81'
session_id:
    description:
        - newly created API session id for given user
    type: str
    returned: always
"""


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        host=dict(type="str", required=True),
        port=dict(type="int", required=False, default=80),
        path=dict(type="str", required=False, default="/api/"),
        user=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        s = requests.Session()
        s.headers["Content-Type"] = "application/json"

        result["url"] = urllib.parse.urljoin(
            f"http://{module.params['host']}:{module.params['port']}",
            module.params["path"],
        )
        if not result["url"].endswith("/"):
            result["url"] = result["url"] + "/"

        response = s.get(result["url"] + f"login/?user={module.params['user']}")

        if response.status_code >= 400 or "session_id" not in response.json():
            module.fail_json(
                msg=f"error on creating session: {response.text}",
                **result,
            )

        result["session_id"] = response.json()["session_id"]
        m = hashlib.md5()
        m.update(result["session_id"].encode("utf-8"))
        m.update(module.params["password"].encode("utf-8"))

        data = dict(
            pw=m.hexdigest().lower(),
        )
        response = s.post(
            result["url"] + f"login/?user={module.params['user']}",
            json=data,
        )
        if response.status_code >= 400 or not response.json().get("complete", False):
            module.fail_json(msg=f"login failed: {response.text}", **result)

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Error: {e}", **result)


def main():
    run_module()


if __name__ == "__main__":
    main()

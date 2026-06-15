#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: device

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: create or rename a Device

description:
    - This module is intended to create or rename LPOS Devices

options:
    url:
        description:
            - the full URL of API-Endpoint
        required: true
        type: str
    session_id:
        description:
            - the session-id used for authentication on API-Endpoint
        required: true
        type: str
    mac:
        description:
            - MAC-Address of Device
            - used as primary identifier in this module
            - in hex without colons (e.g. 112233445566)
        required: true
        type: str
    desc:
        description:
            - name (description) of Device
        required: false
        type: str
        default: ""
"""

EXAMPLES = r"""
- name: create device
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: 112233445566
  delegate_to: localhost
  register: device1

- name: name device
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: 112233445566
    name: some device
  delegate_to: localhost
  register: device1

- name: rename device
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: 112233445566
    name: some important device
  delegate_to: localhost
  register: device1
"""

RETURN = r"""
item:
    description:
        - the item corresponding to number created, updated or found in LPOS. might be None in case of errors or deletion
    type: dict or None
    returned: always
"""


def data_as_expected(d1, d2):
    keys = [
        "mac",
        "desc",
    ]
    for k in keys:
        if k not in d1:
            return False
        if k not in d2:
            return False
        if not d1.get(k) == d2.get(k):
            return False
    return True


def search(url, session, desc):
    uri = f"{url}/device/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}/device/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}/device/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True, no_log=True),
        mac=dict(type="str", required=True),
        desc=dict(type="str", required=False, default=""),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        item=None,
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
        url = module.params["url"]
        session = requests.Session()
        session.headers["Content-Type"] = "application/json"
        session.cookies["LPOSsession"] = module.params["session_id"]

        success, item = search(url, session, module.params["desc"])
        if not success:
            module.fail_json(msg=f"error on searching for item: {item}", **result)

        data = dict(
            id=None,
            mac=module.params["mac"],
            desc=module.params["desc"],
        )

        if item is None:
            if not module.check_mode:
                success, item = create(url, session, data)
                if not success:
                    module.fail_json(
                        msg=f"error on createing new item: {item}",
                        **result,
                    )
                result["changed"] = True
                result["item"] = item
                module.exit_json(msg=f"created item: {item['id']}", **result)
            else:
                result["changed"] = True
                result["item"] = data
                module.exit_json(msg="would have created a item", **result)

        else:
            data["id"] = item["id"]
            if not module.check_mode:
                if data_as_expected(data, item):
                    result["item"] = item
                    module.exit_json(
                        msg=f"item is already as expected: {item['id']}",
                        **result,
                    )
                success, item = update(url, session, data)
                if not success:
                    module.fail_json(
                        msg=f"error on updateing existing item: {item}",
                        **result,
                    )
                result["changed"] = True
                result["item"] = item
                module.exit_json(msg=f"updated item: {item['id']}", **result)
            else:
                result["changed"] = True
                result["item"] = data
                module.exit_json(
                    msg=f"would have updated item: {item['id']}",
                    **result,
                )

    except Exception as e:
        module.fail_json(msg=f"Error: {e}", **result)


def main():
    run_module()


if __name__ == "__main__":
    main()

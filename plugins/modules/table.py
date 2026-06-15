#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: table

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: create, update or delete a Table

description:
    - This module creates, updates, deletes or just returns a LPOS Table configuration

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
    number:
        description:
            - number of Table
            - used as primary identifier in this module
        required: true
        type: int
    desc:
        description:
            - description for Table
        required: false
        type: str
        default: ""
    switch:
        description:
            - name (desc) of Switch providing Ports for this Table
        required_id: state == present
        type: str
        default: None
    seat_ip_pool:
        description:
            - name (desc) of IpPool used for Seats on this Table
        required_if: state == present
        type: str
        default: None
    add_ip_pool:
        description:
            - name (desc) of IpPool used for additional Devices on this Table
        required_if: state == present
        type: str
        default: None
    state:
        description:
            - if IpPool should be created or deleted
        required: false
        type: str
        default: 'present'
        choices: ["absent", "present"]
"""

EXAMPLES = r"""
- name: create table
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    desc: Table 1
    seat_ip_pool: table1-pool
    add_ip_pool: addi-pool
    switch: switch1
    state: present
  delegate_to: localhost
  register: table1

- name: edit table
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    desc: Table 1
    seat_ip_pool: table1-pool
    add_ip_pool: addi-pool
    switch: switch2
    state: present
  delegate_to: localhost
  register: table1

- name: delete table
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    state: absent
  delegate_to: localhost
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
        "number",
        "desc",
        "switch_id",
        "seat_ip_pool_id",
        "add_ip_pool_id",
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
    uri = f"{url}/table/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}/table/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}/table/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def delete(url, session, data):
    uri = f"{url}/table/{data['id']}"

    response = session.delete(uri)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def get_switch_id(url, session, desc):
    uri = f"{url}/switch/"
    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)
    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item["id"])
    return (False, f"Switch with desc '{desc}' not found")


def get_ippool_id(url, session, desc):
    uri = f"{url}/ippool/"
    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)
    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item["id"])
    return (False, f"IpPool with desc '{desc}' not found")


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True, no_log=True),
        number=dict(type="int", required=True),
        desc=dict(type="str", required=False, default=""),
        switch=dict(type="str", required=False, default=None),
        seat_ip_pool=dict(type="str", required=False, default=None),
        add_ip_pool=dict(type="str", required=False, default=None),
        state=dict(type="str", default="present", choices=["absent", "present"]),
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
        required_if=[
            ("state", "present", ("switch", "seat_ip_pool", "add_ip_pool"), False),
        ],
    )

    try:
        url = module.params["url"]
        session = requests.Session()
        session.headers["Content-Type"] = "application/json"
        session.cookies["LPOSsession"] = module.params["session_id"]

        success, item = search(url, session, module.params["desc"])
        if not success:
            module.fail_json(msg=f"error on searching for item: {item}", **result)

        if module.params["state"] == "present":
            success, switch_id = get_switch_id(
                url,
                session,
                module.params["switch"],
            )
            if not success:
                module.fail_json(msg=switch_id, **result)

            success, seat_ip_pool_id = get_ippool_id(
                url,
                session,
                module.params["seat_ip_pool"],
            )
            if not success:
                module.fail_json(msg=seat_ip_pool_id, **result)

            success, add_ip_pool_id = get_ippool_id(
                url,
                session,
                module.params["add_ip_pool"],
            )
            if not success:
                module.fail_json(msg=add_ip_pool_id, **result)

            data = dict(
                id=None,
                number=module.params["number"],
                desc=module.params["desc"],
                switch_id=switch_id,
                seat_ip_pool_id=seat_ip_pool_id,
                add_ip_pool_id=add_ip_pool_id,
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

        else:
            if item is None:
                module.exit_json(msg="item is already deleted", **result)
            if not module.check_mode:
                success, item = delete(url, session, item)
                if not success:
                    module.fail_json(msg=f"error on deleteing item: {item}", **result)
                result["changed"] = True
                module.exit_json(msg="deleted item", **result)
            else:
                result["changed"] = True
                module.exit_json(msg="would have deleted a item", **result)

    except Exception as e:
        module.fail_json(msg=f"Error: {e}", **result)


def main():
    run_module()


if __name__ == "__main__":
    main()

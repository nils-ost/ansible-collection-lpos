#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: ippool

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: create, update or delete an IpPool

description:
    - This module creates, updates, deletes or just returns an LPOS IpPool

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
    desc:
        description:
            - description for IpPool
            - used as primary identifier in this module
        required: true
        type: str
    range_start:
        description:
            - first IP of pool, defines start of range
            - IP in dotted notation, e.g. 127.0.0.1
        required_if: state == present
        type: str
        default: None
    range_end:
        description:
            - last IP of pool, defines end of range
            - IP in dotted notation, e.g. 127.0.0.1
        required_if: state == present
        type: str
        default: None
    mask:
        description:
            - network mask according to range
        required_if: false
        type: int
        default: 24
    vlan_number:
        description:
            - VLAN number (not ID) of VLAN this IpPool belongs to
        required_if: state == present
        type: int
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
- name: create ippool
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: table1-play
    range_start: 192.168.123.10
    range_end: 192.168.123.15
    mask: 24
    vlan_number: 12
    state: present
  delegate_to: localhost
  register: pool1

- name: edit ippool
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: table1-play
    range_start: 192.168.123.10
    range_end: 192.168.123.19
    mask: 24
    vlan_number: 12
    state: present
  delegate_to: localhost
  register: pool1

- name: delete ippool
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: table1-play
    state: absent
  delegate_to: localhost
"""

RETURN = r"""
item:
    description:
        - the item corresponding to description created, updated or found in LPOS. might be None in case of errors or deletion
    type: dict or None
    returned: always
"""


def data_as_expected(d1, d2):
    keys = [
        "desc",
        "mask",
        "range_start",
        "range_end",
        "vlan_id",
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
    uri = f"{url}/ippool/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}/ippool/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}/ippool/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def delete(url, session, data):
    uri = f"{url}/ippool/{data['id']}"

    response = session.delete(uri)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def get_vlan_id(url, session, number):
    uri = f"{url}/vlan/"
    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)
    for item in response.json():
        if number == item.get("number", 0):
            return (True, item["id"])
    return (False, f"VLAN with number '{number}' not found")


def ip_octetts_to_int(oct1, oct2, oct3, oct4):
    r = list()
    r.append(hex(oct1).replace("0x", ""))
    r.append(hex(oct2).replace("0x", ""))
    r.append(hex(oct3).replace("0x", ""))
    r.append(hex(oct4).replace("0x", ""))
    for idx in range(4):
        if len(r[idx]) < 2:
            r[idx] = "0" + r[idx]
    return int("".join(r), 16)


def ip_dotted_to_int(str_input):
    str_input = str_input.split("/")[0]
    return ip_octetts_to_int(*[int(o) for o in str_input.split(".")])


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True, no_log=True),
        desc=dict(type="str", required=True),
        range_start=dict(type="str", required=False, default=None),
        range_end=dict(type="str", required=False, default=None),
        mask=dict(type="int", required=False, default=24),
        vlan_number=dict(type="int", required=False, default=None),
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
            ("state", "present", ("range_start", "range_end", "vlan_id"), False),
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
            vlan_id = None
            success, vlan_id = get_vlan_id(
                url,
                session,
                module.params["vlan_number"],
            )
            if not success:
                module.fail_json(msg=vlan_id, **result)

            range_start = ip_dotted_to_int(module.params["range_start"])
            range_end = ip_dotted_to_int(module.params["range_end"])

            data = dict(
                id=None,
                desc=module.params["desc"],
                range_start=range_start,
                range_end=range_end,
                mask=module.params["mask"],
                vlan_id=vlan_id,
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

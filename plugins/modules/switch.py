#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: switch

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: create, update or delete Switch configuration

description:
    - This module creates, updates, deletes or just returns a LPOS Switch configuration

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
            - description for VLAN
            - used as primary identifier in this module
        required: true
        type: str
    addr:
        description:
            - IP or DNS name to connect to Switch
        required_if: state == present
        type: str
        default: ""
    user:
        description:
            - username used for login on Switch
        required_if: state == present
        type: str
        default: admin
    pw:
        description:
            - passwod used for login on Switch
        required_if: state == present
        type: str
        default: ""
    purpose:
        description:
            - defines the class of the Switch
        required: false
        type: str
        default: core
        choices: ["core", "participants", "mixed"]
    onboarding_vlan_number:
        description:
            - VLAN number (not ID) of VLAN to be used for onboarding network on this Switch
            - not required for Switches with purpose "core"
        required_if: purpose in ["participants", "mixed"]
        type: int
        default: None
    port_numbering_offset:
        description:
            - used to align the numbering of Ports in the frontend
        required: false
        type: int
        default: 0
    state:
        description:
            - if Switch should be created or deleted
        required: false
        type: str
        default: 'present'
        choices: ["absent", "present"]
"""

EXAMPLES = r"""
# create Switch
- name: create switch
  nils_ost.lpos.switch:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: switch1
    addr: 127.0.0.1
    user: admin
    pw: password
    purpose: participants
    onboarding_vlan_number: 10
    state: present
  delegate_to: localhost
  register: switch1

# change the onboarding_vlan and numbering_offset of switch1
- name: update description
  nils_ost.lpos.switch:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: switch1
    addr: 127.0.0.1
    user: admin
    pw: password
    purpose: participants
    onboarding_vlan_number: 11
    port_numbering_offset: 1
    state: present
  delegate_to: localhost
  register: switch1

# delete the formaly created and updated switch1
- name: delete switch
  nils_ost.lpos.switch:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: switch1
    state: absend
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
        "desc",
        "addr",
        "user",
        "purpose",
        "onboarding_vlan_id",
        "port_numbering_offset",
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
    uri = f"{url}/switch/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}/switch/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}/switch/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def delete(url, session, data):
    uri = f"{url}/switch/{data['id']}"

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


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True, no_log=True),
        desc=dict(type="str", required=True),
        addr=dict(type="str", required=False, default=""),
        user=dict(type="str", required=False, default="admin"),
        pw=dict(type="str", required=False, default="", no_log=True),
        purpose=dict(
            type="str",
            required=False,
            default="core",
            choices=["core", "participants", "mixed"],
        ),
        onboarding_vlan_number=dict(type="int", required=False, default=None),
        port_numbering_offset=dict(type="int", required=False, default=0),
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
            ("state", "present", ("addr", "user", "pw"), False),
            ("purpose", "participants", ("onboarding_vlan_number")),
            ("purpose", "mixed", ("onboarding_vlan_number")),
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
            purposes = dict(
                core=0,
                participants=1,
                mixed=2,
            )

            vlan_id = None
            if purposes[module.params["purpose"]] > 0:
                success, vlan_id = get_vlan_id(
                    url,
                    session,
                    module.params["onboarding_vlan_number"],
                )
                if not success:
                    module.fail_json(msg=vlan_id, **result)

            data = dict(
                id=None,
                desc=module.params["desc"],
                addr=module.params["addr"],
                user=module.params["user"],
                pw=module.params["pw"],
                purpose=purposes[module.params["purpose"]],
                onboarding_vlan_id=vlan_id,
                port_numbering_offset=module.params["port_numbering_offset"],
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

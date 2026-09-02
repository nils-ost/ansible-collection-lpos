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
    - This module manages LPOS Device elements via the LPOS REST API.
    - A Device represents a network-connected device detected on a MikroTik switch port.
    - Devices are identified by their MAC address (unique, stored without colons) in the LPOS backend.
    - The module supports create and update operations.
    - When creating or updating, the module searches for an existing device by its MAC address (I(mac)) via the LPOS API.
      If found, it updates the existing record with the provided I(desc) with the provided I(desc); otherwise it creates a new one.
    - The MAC address is sent to the LPOS backend as part of the create/update payload — the backend enforces uniqueness on this field.

options:
    state:
        description:
            - Whether the Device should exist (present) or be removed (absent).
        required: false
        type: str
        choices: [ present, absent ]
        default: present
    url:
        description:
            - The full base URL of the LPOS API endpoint (e.g. C(http://192.168.0.5:81/api/)).
        required: true
        type: str
    session_id:
        description:
            - A valid session ID obtained from a previous login via the C(login) module.
        required: true
        type: str
    mac:
        description:
            - MAC address of the device. Required when C(state=present) or when deleting with C(state=absent).
            - Must be in hexadecimal format without colons (e.g., C(112233445566)).
            - The LPOS backend enforces uniqueness on this field — no two devices can share the same MAC.
        required: true
        type: str
    desc:
        description:
            - Human-readable description (name) of the device. Used to set or rename the device on creation/update
            - When a device is assigned to a seat in LPOS, this field may be auto-set from the Participant's name by the backend.
        required: false
        type: str
        default: ""

notes:
    - The module searches for existing devices by their C(mac) field.
      If a device with that MAC already exists, it is updated with the provided I(desc); otherwise a new device is created.
    - No two devices can have the same MAC address.
    - The LPOS backend automatically calculates several fields when certain parameters are set

seealso:
    - module: nils_ost.lpos.login
    - module: nils_ost.lpos.ippool
    - module: nils_ost.lpos.table
    - module: nils_ost.lpos.switch
"""

EXAMPLES = r"""
- name: create a device with minimal parameters
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: aabbccddeeff
  delegate_to: localhost
  register: new_device

- name: create a device with description
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: aabbccddeeff
    desc: John's Laptop
  delegate_to: localhost
  register: new_device

- name: update device description (finds existing by desc, updates mac)
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: aabbccddeeff
    desc: Updated Device Name
  delegate_to: localhost
  register: updated_device

- name: delete a device by description and MAC
  nils_ost.lpos.device:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    mac: aabbccddeeff
    desc: Device to Remove
    state: absent
  delegate_to: localhost
  register: deleted_device
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


def search(url, session, mac):
    uri = f"{url}device/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if mac == item.get("mac", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}device/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}device/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 201:
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

        success, item = search(url, session, module.params["mac"])
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
                result["item"] = item["created"]
                module.exit_json(msg=f"created item: {item['created']}", **result)
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
                result["item"] = item["updated"]
                module.exit_json(msg=f"updated item: {item['updated']}", **result)
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

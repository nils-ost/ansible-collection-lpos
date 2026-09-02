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
    - This module manages LPOS IpPool elements via the LPOS REST API.
    - An IpPool defines a range of IP addresses within a VLAN that can be assigned to devices (seats, additional devices).
    - The module supports create, update, and delete operations. For deletion, use C(state=absent) with the I(desc) parameter.
    - When creating or updating, the module searches for an existing IpPool by its description (I(desc)) field.
      If found, it updates the existing record; otherwise it creates a new one.
    - IP addresses are stored internally as integers. The module accepts IPs in dotted notation (e.g., C(192.168.1.10))
      and converts them automatically.
    - Each IpPool belongs to exactly one VLAN, referenced by I(vlan_number) which is resolved to the VLAN's MongoDB _id.
    - The VLAN must already exist before creating an IpPool for it.
    - For VLANs with purpose 1 (mgmt) or 2 (onboarding), only ONE IpPool per VLAN is allowed.
      VLANs with purpose 0 (play) can have multiple IpPools.

options:
    state:
        description:
            - Whether the IpPool should exist (present) or be removed (absent).
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
    desc:
        description:
            - Human-readable description of the IP pool. Used as the lookup key to find existing IpPools for update operations.
            - Examples: C(table1-play), C(mgmt-pool), C(onboarding-range).
        required: true
        type: str
    range_start:
        description:
            - First IP address of the pool range (start of the assignable IP range).
            - Must be in dotted decimal notation (e.g., C(192.168.1.10)).
            - The IP must fall within the subnet defined by I(mask) and cannot overlap with another IpPool on the same VLAN.
        required_if:
            - [ present, range_start ]
            - [ present, range_end ]
            - [ present, vlan_number ]
        type: str
    range_end:
        description:
            - Last IP address of the pool range (end of the assignable IP range).
            - Must be in dotted decimal notation (e.g., C(192.168.1.50)).
            - Must be greater than or equal to I(range_start) and within the subnet defined by I(mask).
        required_if:
            - [ present, range_start ]
            - [ present, range_end ]
            - [ present, vlan_number ]
        type: str
    mask:
        description:
            - CIDR prefix length (subnet mask) for the IP pool.
            - Must be between 8 and 30 inclusive.
            - The mask must encompass both I(range_start) and I(range_end) — all IPs in the range must fall within the same subnet.
            - Default is C(24), which provides 254 usable addresses (excluding network and broadcast).
        required: false
        type: int
        default: 24
    vlan_number:
        description:
            - The VLAN number (not MongoDB _id) of the VLAN this IpPool belongs to.
            - The module resolves this VLAN number to its MongoDB _id via the LPOS VLAN API before creating/updating the IpPool.
            - For play networks (VLAN purpose 0), multiple IpPools can share the same VLAN.
            - For mgmt (purpose 1) and onboarding (purpose 2) VLANs, only one IpPool is allowed per VLAN.
        required_if:
            - [ present, range_start ]
            - [ present, range_end ]
            - [ present, vlan_number ]
        type: int

notes:
    - The module searches for existing IpPools by their C(desc) field. If multiple pools share the same description, only the first match is updated.
    - The I(vlan_number) is resolved via the LPOS VLAN API — the referenced VLAN must already exist before this module runs.
    - Validation error codes. 30 (mask must be between 8 and 30), 31 (mask does not fit range_start and range_end — IPs outside subnet),
      32 (range_start must be smaller than or equal to range_end), 33 (IP range overlaps with an existing IpPool),
      34 (invalid IP address — out of valid range 01000000 to FFFFFEFD), 39 (only one IpPool allowed for mgmt/onboarding VLANs).
    - Deleting an IpPool that is referenced by a Table will fail with an error from the API.
    - The C(range_start) and I(range_end) IPs are stored as integers internally. The module handles conversion automatically.

seealso:
    - module: nils_ost.lpos.login
    - module: nils_ost.lpos.vlan
    - module: nils_ost.lpos.table
"""

EXAMPLES = r"""
- name: create a play network IP pool
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: table1-play
    range_start: 192.168.123.10
    range_end: 192.168.123.50
    mask: 24
    vlan_number: 10
    state: present
  delegate_to: localhost
  register: play_pool

- name: create a management network IP pool (single per mgmt VLAN)
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: mgmt-pool
    range_start: 10.0.0.10
    range_end: 10.0.0.50
    mask: 24
    vlan_number: 20
    state: present
  delegate_to: localhost
  register: mgmt_pool

- name: create an onboarding network IP pool (single per onboarding VLAN)
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: onboarding-range
    range_start: 172.16.0.10
    range_end: 172.16.0.100
    mask: 24
    vlan_number: 30
    state: present
  delegate_to: localhost
  register: ob_pool

- name: create a small IP pool with /28 mask (14 usable addresses)
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: small-pool
    range_start: 192.168.50.1
    range_end: 192.168.50.14
    mask: 28
    vlan_number: 10
    state: present
  delegate_to: localhost
  register: small_pool

- name: update an existing IP pool by description
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: table1-play
    range_start: 192.168.123.10
    range_end: 192.168.123.100
    mask: 24
    vlan_number: 10
    state: present
  delegate_to: localhost
  register: updated_pool

- name: delete an IP pool by description
  nils_ost.lpos.ippool:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    desc: table1-play
    state: absent
  delegate_to: localhost
  register: deleted_pool
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
    uri = f"{url}ippool/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}ippool/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}ippool/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def delete(url, session, data):
    uri = f"{url}ippool/{data['id']}"

    response = session.delete(uri)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def get_vlan_id(url, session, number):
    uri = f"{url}vlan/"
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
            ("state", "present", ("range_start", "range_end", "vlan_number"), False),
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

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
    - This module manages LPOS Table elements via the LPOS REST API.
    - A Table represents a physical arrangement of seats on MikroTik switch ports. Each table has a unique number,
      is associated with a specific switch, and defines two IP pools. one for seat devices (play network) and
      one for additional devices connected to the same table.
    - The module supports create, update, and delete operations. For deletion, use C(state=absent) with the I(number) parameter.
    - When creating or updating, the module searches for an existing Table by its number (I(number)) via the LPOS API.
      If found, it updates the existing record with the provided parameters; otherwise it creates a new one.
    - The switch referenced by I(switch) must have purpose 1 (participant) or 2 (mixed). Core switches
      (purpose 0) cannot host tables.
    - Both IP pools (I(seat_ip_pool) and I(add_ip_pool)) must belong to VLANs with purpose 0 (play/seats).
    - The two IP pools must be different — the same pool cannot be used for both seat devices and additional devices
      on the same table. Additionally, each pool can only serve one role. a pool assigned as C(seat_ip_pool_id)
      to one Table cannot be used as C(add_ip_pool_id) by another Table (and vice versa).
    - The module resolves switch descriptions and IP pool descriptions to their MongoDB _ids via the LPOS API
      before creating/updating the table.

options:
    state:
        description:
            - Whether the Table should exist (present) or be removed (absent).
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
    number:
        description:
            - Unique table number. Used as the primary identifier for lookup and must be unique across all tables in LPOS.
            - Must be greater than or equal to 0.
            - Required when C(state=present) or when deleting with C(state=absent).
        required: true
        type: int
    desc:
        description:
            - Human-readable description of the table. Used to set or rename the table on creation/update.
            - Examples: C(Table 1), C(Stage A), C(Room B-Row3).
        required: false
        type: str
        default: ""
    switch:
        description:
            - Description (I(desc) field) of the Switch that provides ports for this table.
            - The referenced switch must have I(purpose) set to 1 (participant) or 2 (mixed).
              Core switches (purpose 0) cannot host tables.
            - The module resolves this description to the switch's MongoDB _id via the LPOS Switch API.
        required_if:
            - [ present, switch ]
            - [ present, seat_ip_pool ]
            - [ present, add_ip_pool ]
        type: str
    seat_ip_pool:
        description:
            - Description (I(desc) field) of the IpPool used for seat devices on this table.
            - The referenced IpPool must belong to a VLAN with purpose 0 (play/seats).
            - This pool defines the IP range assigned to each seat. C(ip = range_start + seat_number - 1).
            - Once assigned, this pool cannot be used as I(add_ip_pool) on any other table.
        required_if:
            - [ present, switch ]
            - [ present, seat_ip_pool ]
            - [ present, add_ip_pool ]
        type: str
    add_ip_pool:
        description:
            - Description (I(desc) field) of the IpPool used for additional (non-seat) devices on this table.
            - Additional devices are extra devices connected to a table beyond their assigned seat.
            - The referenced IpPool must belong to a VLAN with purpose 0 (play/seats).
            - Once assigned, this pool cannot be used as I(seat_ip_pool) on any other table.
        required_if:
            - [ present, switch ]
            - [ present, seat_ip_pool ]
            - [ present, add_ip_pool ]
        type: str

notes:
    - The module searches for existing tables by their C(number) field.
      If a table with that number already exists, it is updated with the provided parameters; otherwise a new table is created.
    - Both I(seat_ip_pool) and I(add_ip_pool) must be different — using the same pool for both will fail validation.
    - Each IP pool can only serve one role across all tables. a pool assigned as C(seat_ip_pool_id) to one table
      cannot be used as C(add_ip_pool_id) on another, and vice versa.
    - The I(switch), I(seat_ip_pool), and I(add_ip_pool) parameters are resolved via the LPOS API — these resources
      must already exist before this module runs.
    - Validation error codes. 40 (number must be >= 0), 41 (FK not found — switch, seat_ip_pool, or add_ip_pool does not exist),
      42 (switch purpose must be 1 or 2, not 0/core), 43 (IP pool VLAN purpose must be 0/play),
      44 (seat_ip_pool already in use as add_ip_pool on another table), 45 (both pools cannot be the same),
      46 (add_ip_pool already in use as seat_ip_pool on another table).
    - Deleting a table that has associated Seats will fail with an error from the API.

seealso:
    - module: nils_ost.lpos.login
    - module: nils_ost.lpos.switch
    - module: nils_ost.lpos.ippool
    - module: nils_ost.lpos.seat
"""

EXAMPLES = r"""
- name: create a table with full configuration
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    desc: Table 1
    seat_ip_pool: table1-pool
    add_ip_pool: additional-devices-pool
    switch: participant-switch-1
    state: present
  delegate_to: localhost
  register: new_table

- name: create multiple tables on the same switch
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: "{{ item.number }}"
    desc: "Table {{ item.number }}"
    seat_ip_pool: "table{{ item.number }}-pool"
    add_ip_pool: additional-devices-pool
    switch: participant-switch-1
    state: present
  delegate_to: localhost
  loop:
    - { number: 2, desc: "Table 2" }
    - { number: 3, desc: "Table 3" }
  register: multiple_tables

- name: create a table with different pools for seats and additional devices
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 5
    desc: Conference Room A
    seat_ip_pool: conf-a-seats
    add_ip_pool: conf-a-additional
    switch: mixed-switch-2
    state: present
  delegate_to: localhost
  register: conf_table

- name: update a table by changing its switch assignment
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    desc: Table 1
    seat_ip_pool: table1-pool
    add_ip_pool: additional-devices-pool
    switch: participant-switch-2
    state: present
  delegate_to: localhost
  register: updated_table

- name: update a table description only
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    desc: Main Stage Table 1
    seat_ip_pool: table1-pool
    add_ip_pool: additional-devices-pool
    switch: participant-switch-1
    state: present
  delegate_to: localhost
  register: renamed_table

- name: delete a table by number
  nils_ost.lpos.table:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    number: 1
    state: absent
  delegate_to: localhost
  register: deleted_table
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


def search(url, session, number):
    uri = f"{url}table/"

    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)

    for item in response.json():
        if number == item.get("number", ""):
            return (True, item)
    return (True, None)


def create(url, session, data):
    uri = f"{url}table/"

    response = session.post(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def update(url, session, data):
    uri = f"{url}table/{data['id']}/"

    response = session.patch(uri, json=data)
    if not response.status_code == 201:
        return (False, response.text)
    return (True, response.json())


def delete(url, session, data):
    uri = f"{url}table/{data['id']}"

    response = session.delete(uri)
    if not response.status_code == 200:
        return (False, response.text)
    return (True, response.json())


def get_switch_id(url, session, desc):
    uri = f"{url}switch/"
    response = session.get(uri)
    if not response.status_code == 200:
        return (False, response.text)
    for item in response.json():
        if desc == item.get("desc", ""):
            return (True, item["id"])
    return (False, f"Switch with desc '{desc}' not found")


def get_ippool_id(url, session, desc):
    uri = f"{url}ippool/"
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

        success, item = search(url, session, module.params["number"])
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

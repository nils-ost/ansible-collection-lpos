#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: list

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: returns a list of all LPOS elements of a given kind

description:
    - This module retrieves a list of all existing elements of a specified kind from the LPOS REST API.
    - The LPOS backend exposes element lists via plain GET requests to C(GET /api/{element}/).
    - Supported element types are C(vlan), C(ippool), C(switch), C(table), C(seat), C(participant), C(device), and C(port).
    - A valid session_id from the C(login) module is required for authentication.

options:
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
    element:
        description:
            - The element kind to list.
            - Supported values are C(vlan), C(ippool), C(switch), C(table), C(seat), C(participant), C(device), and C(port).
        required: true
        type: str
        choices: [ vlan, ippool, switch, table, seat, participant, device, port ]

requirements: [ "requests" ]
"""

EXAMPLES = r"""
- name: list all VLANs
  nils_ost.lpos.list:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    element: vlan
  delegate_to: localhost
  register: vlans

- name: list all switches
  nils_ost.lpos.list:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    element: switch
  delegate_to: localhost
  register: switches

- name: iterate over all devices
  nils_ost.lpos.list:
    url: "{{ lpos.url }}"
    session_id: "{{ lpos.session_id }}"
    element: device
  delegate_to: localhost
  register: devices

- name: list all devices and print their MAC addresses
  ansible.builtin.debug:
    msg: "{{ item.mac }}"
  loop: "{{ devices.items }}"
  no_log: true
"""

RETURN = r"""
items:
    description:
        - A list of all element objects of the requested kind returned from the LPOS API.
        - Each item is a dictionary containing the element's attributes as returned by the backend.
    type: list
    returned: always
    sample:
      [
        { "id": "507f1f77bcf86cd799439011", "number": 10, "purpose": 0, "desc": "Play network" },
        { "id": "507f1f77bcf86cd799439012", "number": 20, "purpose": 2, "desc": "Onboarding" }
      ]
count:
    description:
        - The number of elements returned in the list.
    type: int
    returned: always
"""


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True, no_log=True),
        element=dict(
            type="str",
            required=True,
            choices=[
                "vlan",
                "ippool",
                "switch",
                "table",
                "seat",
                "participant",
                "device",
                "port",
            ],
        ),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        items=[],
        count=0,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        session = requests.Session()
        session.cookies.set("LPOSsession", module.params["session_id"])
        session.headers["Content-Type"] = "application/json"

        url = module.params["url"]
        element = module.params["element"]

        response = session.get(url + element + "/")
        if response.status_code >= 400:
            module.fail_json(
                msg=f"failed to list {element} elements: HTTP {response.status_code} - {response.text}",
                **result,
            )

        items = response.json()
        result["items"] = items
        result["count"] = len(items)
        module.exit_json(**result)

    except requests.exceptions.ConnectionError as e:
        module.fail_json(
            msg=f"failed to connect to LPOS API at {url}: {str(e)}",
            **result,
        )
    except requests.exceptions.Timeout:
        module.fail_json(
            msg=f"connection to LPOS API at {url} timed out",
            **result,
        )
    except Exception as e:
        module.fail_json(
            msg=f"unexpected error listing {element} elements: {str(e)}",
            **result,
        )


def main():
    run_module()


if __name__ == "__main__":
    main()

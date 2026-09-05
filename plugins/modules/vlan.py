#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: vlan

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: creates, updates or deletes VLANs on an LPOS instance

description:
    - Manages VLAN elements on a LanPartyOnboardingSystem (LPOS) instance via its REST API.
    - VLANs are used to define network segments for play, management, onboarding, and other purposes.
    - A valid session_id from the C(login) module is required for authentication.

options:
    state:
        description:
            - Whether the VLAN should exist (present) or be removed (absent).
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
            - The VLAN ID (1-1024). Required when C(state=present) or when deleting a specific VLAN with C(state=absent).
            - Must be unique and not already in use by another VLAN.
        required: true
        type: int
    purpose:
        description:
            - The purpose of the VLAN.
            - Values 0 (play) and 1 (mgmt) must be unique across all VLANs — only one each allowed.
            - Value 2 is for onboarding networks (multiple allowed, one per switch).
            - Value 3 is for other purposes.
        required: false
        type: int
        choices: [ 0, 1, 2, 3 ]
        default: 3
    desc:
        description:
            - A human-readable description of the VLAN.
        required: false
        type: str
        default: ""

notes:
    - Deleting a VLAN that has associated IpPools or Switch references will fail with an error from the API.
    - When C(state=present) and C(number) matches an existing VLAN, the module updates it if any attributes differ.
    - This module requires a valid session cookie passed via the C(session_id).

requirements: [ "requests" ]
"""

EXAMPLES = r"""
# Create a new play network VLAN with ID 10
- name: create play VLAN
  nils_ost.lpos.vlan:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: present
    number: 10
    purpose: 0
    desc: "Play network"

# Create an onboarding VLAN with ID 20
- name: create onboarding VLAN
  nils_ost.lpos.vlan:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: present
    number: 20
    purpose: 2
    desc: "Onboarding network for switch1"

# Update an existing VLAN's description
- name: update VLAN description
  nils_ost.lpos.vlan:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: present
    number: 10
    desc: "Updated play network description"

# Delete a VLAN
- name: delete onboarding VLAN
  nils_ost.lpos.vlan:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: absent
    number: 20
"""

RETURN = r"""
vlan:
    description:
        - The full VLAN object returned from the API (for present state) or None (for absent).
    type: dict
    returned: when state is 'present' and succeeded
    sample: { "id": "...", "number": 10, "purpose": 0, "desc": "Play network" }

vlan_id:
    description:
        - The MongoDB _id of the VLAN element.
    type: str
    returned: when state is 'present' and succeeded
"""


def get_vlan_by_number(session, url, number):
    """Look up an existing VLAN by its number via GET /vlan/."""
    response = session.get(url + "vlan/")
    if response.status_code >= 400:
        return None
    vlans = response.json()
    for v in vlans:
        if v.get("number") == number:
            return v
    return None


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        state=dict(
            type="str",
            required=False,
            choices=["present", "absent"],
            default="present",
        ),
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True),
        number=dict(type="int", required=True),
        purpose=dict(type="int", required=False, default=3, choices=[0, 1, 2, 3]),
        desc=dict(type="str", required=False, default=""),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        vlan=None,
        vlan_id=None,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        session = requests.Session()
        # Pass session_id as a cookie for authentication
        session.cookies.set("LPOSsession", module.params["session_id"])
        session.headers["Content-Type"] = "application/json"

        url = module.params["url"]
        state = module.params.get("state", "present")
        number = module.params.get("number")
        purpose = module.params.get("purpose", 3)
        desc = module.params.get("desc", "")

        if state == "present":
            # --- CREATE / UPDATE mode ---
            existing = get_vlan_by_number(session, url, number)

            if existing is None:
                # VLAN does not exist — create it
                if module.check_mode:
                    result["changed"] = True
                    result["vlan"] = {
                        "number": number,
                        "purpose": purpose,
                        "desc": desc,
                    }
                    module.exit_json(**result)

                data = dict(
                    number=number,
                    purpose=purpose,
                    desc=desc,
                )
                response = session.post(url + "vlan/", json=data)
                if response.status_code >= 400:
                    module.fail_json(
                        msg=f"failed to create VLAN {number}: {response.text}",
                        **result,
                    )

                created = response.json()
                result["changed"] = True
                result["vlan"] = created
                result["vlan_id"] = created.get("id")
                module.exit_json(**result)

            else:
                # VLAN exists — check if update is needed
                needs_update = False
                updated_data = dict()

                if existing.get("purpose") != purpose:
                    needs_update = True
                    updated_data["purpose"] = purpose

                if existing.get("desc") != desc:
                    needs_update = True
                    updated_data["desc"] = desc

                if not needs_update:
                    result["vlan"] = existing
                    result["vlan_id"] = existing.get("id")
                    module.exit_json(**result)

                # Update needed
                if module.check_mode:
                    result["changed"] = True
                    result["vlan"] = {**existing, **updated_data}
                    module.exit_json(**result)

                updated_data["id"] = existing["id"]
                response = session.patch(
                    url + "vlan/" + existing["id"] + "/",
                    json=updated_data,
                )
                if response.status_code >= 400:
                    module.fail_json(
                        msg=f"failed to update VLAN {number}: {response.text}",
                        **result,
                    )

                updated = response.json()
                result["changed"] = True
                result["vlan"] = updated
                result["vlan_id"] = updated.get("id")
                module.exit_json(**result)

        elif state == "absent":
            # --- DELETE mode ---
            existing = get_vlan_by_number(session, url, number)

            if existing is None:
                # VLAN does not exist — nothing to do
                module.exit_json(**result)

            if module.check_mode:
                result["changed"] = True
                result["vlan"] = existing
                module.exit_json(**result)

            response = session.delete(url + "vlan/" + existing["id"])
            if response.status_code >= 400:
                module.fail_json(
                    msg=f"failed to delete VLAN {number}: {response.text}",
                    **result,
                )

            result["changed"] = True
            result["vlan"] = existing
            module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Error: {e}", **result)


def main():
    run_module()


if __name__ == "__main__":
    main()

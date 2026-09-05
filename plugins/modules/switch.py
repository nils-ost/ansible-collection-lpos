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

short_description: creates, updates or deletes Switches on an LPOS instance

description:
    - Manages Switch elements on a LanPartyOnboardingSystem (LPOS) instance via its REST API.
    - Switches represent MikroTik hardware that the LPOS manages for VLAN and port configuration.
    - A valid session_id from the C(login) module is required for authentication.

options:
    state:
        description:
            - Whether the Switch should exist (present) or be removed (absent).
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
    addr:
        description:
            - IP address or hostname of the MikroTik switch. Required when C(state=present) or when deleting a specific switch with C(state=absent).
            - Must be unique — no two switches can share the same address.
        required: true
        type: str
    purpose:
        description:
            - The purpose of the switch.
            - Value 0 = core switch (no onboarding VLAN required).
            - Values 1 and 2 require an C(onboarding_vlan_number) to be specified.
            - Purpose 1 = participant switch, 2 = mixed switch.
        required: false
        type: int
        choices: [ 0, 1, 2 ]
        default: 0
    onboarding_vlan_number:
        description:
            - The VLAN number to use as the onboarding VLAN for this switch.
            - Required when C(purpose) is 1 or 2.
            - The module will resolve this VLAN number to its MongoDB _id via the LPOS API before creating/updating the switch.
            - The referenced VLAN must have purpose=2 (onboarding).
        required: false
        type: int
    desc:
        description:
            - A human-readable description of the switch.
        required: false
        type: str
        default: ""
    user:
        description:
            - username for authenticating to the MikroTik switch.
        required: false
        type: str
        default: "admin"
    pw:
        description:
            - password for authenticating to the MikroTik switch.
        required: false
        type: str
        default: ""
    port_numbering_offset:
        description:
            - Offset added to physical port numbers for display purposes.
        required: false
        type: int
        default: 0

notes:
    - Deleting a switch that has associated Tables will fail with an error from the API.
    - When C(state=present) and C(addr) matches an existing switch, the module updates it if any attributes differ.
    - The C(onboarding_vlan_number) is resolved via the LPOS VLAN API — the VLAN must already exist before this module runs.
    - Switches with purpose 0 (core) automatically have their onboarding VLAN cleared.
    - This module requires a valid session cookie passed via the C(session_id).

requirements: [ "requests" ]
"""

EXAMPLES = r"""
# Create a core switch (no onboarding VLAN needed)
- name: create core switch
  nils_ost.lpos.switch:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: present
    addr: "192.168.1.1"
    purpose: 0
    user: "admin"
    pw: "secret"
    desc: "Core switch"

# Create a participant switch with onboarding VLAN
- name: create participant switch
  nils_ost.lpos.switch:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: present
    addr: "192.168.1.10"
    purpose: 1
    onboarding_vlan_number: 20
    user: "admin"
    pw: "secret"
    desc: "Participant switch hall A"

# Update a switch's description and port numbering offset
- name: update switch
  nils_ost.lpos.switch:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: present
    addr: "192.168.1.1"
    desc: "Updated core switch description"
    port_numbering_offset: 1

# Delete a switch
- name: delete participant switch
  nils_ost.lpos.switch:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: absent
    addr: "192.168.1.10"
"""

RETURN = r"""
switch:
    description:
        - The full Switch object returned from the API (for present state) or None (for absent).
    type: dict
    returned: when state is 'present' and succeeded
    sample: { "id": "...", "addr": "192.168.1.1", "purpose": 0, "desc": "Core switch" }

switch_id:
    description:
        - The MongoDB _id of the Switch element.
    type: str
    returned: when state is 'present' and succeeded
"""


def get_switch_by_addr(session, url, addr):
    """Look up an existing Switch by its address via GET /switch/."""
    response = session.get(url + "switch/")
    if response.status_code >= 400:
        return None
    switches = response.json()
    for s in switches:
        if s.get("addr") == addr:
            return s
    return None


def resolve_vlan_number_to_id(session, url, vlan_number):
    """Resolve a VLAN number to its MongoDB _id via the LPOS VLAN API."""
    response = session.get(url + "vlan/")
    if response.status_code >= 400:
        return None
    vlans = response.json()
    for v in vlans:
        if v.get("number") == vlan_number:
            return v.get("id")
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
        addr=dict(type="str", required=True),
        purpose=dict(type="int", required=False, default=0, choices=[0, 1, 2]),
        onboarding_vlan_number=dict(type="int", required=False),
        desc=dict(type="str", required=False, default=""),
        user=dict(type="str", required=False, default="admin"),
        pw=dict(type="str", required=False, default="", no_log=True),
        port_numbering_offset=dict(type="int", required=False, default=0),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        switch=None,
        switch_id=None,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ["purpose", 1, ["onboarding_vlan_number"]],
            ["purpose", 2, ["onboarding_vlan_number"]],
        ],
    )

    try:
        session = requests.Session()
        # Pass session_id as a cookie for authentication
        session.cookies.set("LPOSsession", module.params["session_id"])
        session.headers["Content-Type"] = "application/json"

        url = module.params["url"]
        state = module.params.get("state", "present")
        addr = module.params.get("addr")
        purpose = module.params.get("purpose", 0)
        onboarding_vlan_number = module.params.get("onboarding_vlan_number")
        desc = module.params.get("desc", "")
        user = module.params.get("user", "admin")
        pw = module.params.get("pw", "")
        port_numbering_offset = module.params.get("port_numbering_offset", 0)

        if state == "present":
            # --- CREATE / UPDATE mode ---

            # Resolve onboarding VLAN number to ID if purpose requires it (1 or 2)
            onboarding_vlan_id = None
            if purpose in [1, 2]:
                onboarding_vlan_id = resolve_vlan_number_to_id(
                    session,
                    url,
                    onboarding_vlan_number,
                )
                if onboarding_vlan_id is None:
                    module.fail_json(
                        msg=f"VLAN with number {onboarding_vlan_number} not found in LPOS",
                        **result,
                    )

            existing = get_switch_by_addr(session, url, addr)

            if existing is None:
                # Switch does not exist — create it
                if module.check_mode:
                    result["changed"] = True
                    result["switch"] = {
                        "addr": addr,
                        "purpose": purpose,
                        "desc": desc,
                        "user": user,
                        "port_numbering_offset": port_numbering_offset,
                    }
                    if onboarding_vlan_id is not None:
                        result["switch"]["onboarding_vlan_id"] = onboarding_vlan_id
                    module.exit_json(**result)

                data = dict(
                    addr=addr,
                    purpose=purpose,
                    desc=desc,
                    user=user,
                    pw=pw,
                    port_numbering_offset=port_numbering_offset,
                )
                if onboarding_vlan_id is not None:
                    data["onboarding_vlan_id"] = onboarding_vlan_id

                response = session.post(url + "switch/", json=data)
                if response.status_code >= 400:
                    module.fail_json(
                        msg=f"failed to create switch '{addr}': {response.text}",
                        **result,
                    )

                created = response.json()
                result["changed"] = True
                result["switch"] = created
                result["switch_id"] = created.get("id")
                module.exit_json(**result)

            else:
                # Switch exists — check if update is needed
                needs_update = False
                updated_data = dict()

                if existing.get("purpose") != purpose:
                    needs_update = True
                    updated_data["purpose"] = purpose

                if existing.get("desc") != desc:
                    needs_update = True
                    updated_data["desc"] = desc

                if existing.get("user") != user:
                    needs_update = True
                    updated_data["user"] = user

                if pw and existing.get("pw") != pw:
                    needs_update = True
                    updated_data["pw"] = pw

                if existing.get("port_numbering_offset") != port_numbering_offset:
                    needs_update = True
                    updated_data["port_numbering_offset"] = port_numbering_offset

                # Handle onboarding VLAN changes
                if purpose in [1, 2]:
                    current_onboard_id = existing.get("onboarding_vlan_id")
                    if current_onboard_id != onboarding_vlan_id:
                        needs_update = True
                        updated_data["onboarding_vlan_id"] = onboarding_vlan_id
                elif purpose == 0:
                    # Core switch — clear onboarding VLAN
                    if existing.get("onboarding_vlan_id") is not None:
                        needs_update = True
                        updated_data["onboarding_vlan_id"] = None

                if not needs_update:
                    result["switch"] = existing
                    result["switch_id"] = existing.get("id")
                    module.exit_json(**result)

                # Update needed
                if module.check_mode:
                    result["changed"] = True
                    result["switch"] = {**existing, **updated_data}
                    module.exit_json(**result)

                updated_data["id"] = existing["id"]
                response = session.patch(
                    url + "switch/" + existing["id"] + "/",
                    json=updated_data,
                )
                if response.status_code >= 400:
                    module.fail_json(
                        msg=f"failed to update switch '{addr}': {response.text}",
                        **result,
                    )

                updated = response.json()
                result["changed"] = True
                result["switch"] = updated
                result["switch_id"] = updated.get("id")
                module.exit_json(**result)

        elif state == "absent":
            # --- DELETE mode ---
            existing = get_switch_by_addr(session, url, addr)

            if existing is None:
                # Switch does not exist — nothing to do
                module.exit_json(**result)

            if module.check_mode:
                result["changed"] = True
                result["switch"] = existing
                module.exit_json(**result)

            response = session.delete(url + "switch/" + existing["id"])
            if response.status_code >= 400:
                module.fail_json(
                    msg=f"failed to delete switch '{addr}': {response.text}",
                    **result,
                )

            result["changed"] = True
            result["switch"] = existing
            module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Error: {e}", **result)


def main():
    run_module()


if __name__ == "__main__":
    main()

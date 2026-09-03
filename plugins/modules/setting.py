#!/usr/bin/python

# Copyright: (c) 2026, Nils Ost <home@nijos.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import requests

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: setting

author: Nils Ost (@nils-ost)

version_added: "1.0.0"

short_description: get or update LPOS system settings

description:
    - Manages LPOS system settings via the LPOS REST API at C(/setting/).
    - Settings are key-value pairs that control various aspects of the LPOS system including network configuration, SSO integration, metrics, and VLAN defaults.
    - A valid session_id from the C(login) module is required for authentication.
    - All settings are readable by any authenticated user.
      Only settings listed in the backend's C(_admin_writeable) list can be modified, and only by admin users.

options:
    state:
        description:
            - Whether to retrieve a setting (C(get)) or update it (C(update)).
        required: false
        type: str
        choices: [ get, update ]
        default: get
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
    key:
        description:
            - The setting key to get or update.
        required: true
        type: str
    value:
        description:
            - The new value to set when C(state=update).
            - Type depends on the setting key.
            - For IP-type settings, pass an integer representing the IP address (use dotted-to-int conversion).
            - For bool settings, use Python-style booleans (true/false in YAML).
            - For int settings, pass a plain integer.
            - For str settings, pass a string.
        required: false
        type: raw

notes:
    - Only admin users can modify settings listed in the backend's C(_admin_writeable) list.
      Non-admin users will receive an authorization error when attempting to update restricted keys.
    - IP-type settings (C(play_ip), C(play_dhcp), etc.) are stored as integers internally. When updating, pass the integer representation of the IP address.
    - Integrity timestamp settings and cached management interface settings (C(lpos_mgmt_mac), C(lpos_mgmt_ip)) are read-only — they are managed by the backend.
    - The module uses a PATCH request to update a single setting key-value pair at C(/setting/{key}/).

seealso:
    - module: nils_ost.lpos.login
"""

EXAMPLES = r"""
# Get a single setting value
- name: get current domain setting
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: get
    key: domain
  delegate_to: localhost
  register: domain_setting

# Get the metrics port
- name: get metrics port
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: get
    key: metrics_port
  delegate_to: localhost
  register: metrics_port_setting

# Enable metrics endpoint
- name: enable Prometheus metrics
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: update
    key: metrics_enabled
    value: true
  delegate_to: localhost
  register: metrics_update

# Disable auto-commits (maintenance mode)
- name: disable auto-commits for maintenance
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: update
    key: disable_auto_commits
    value: true
  delegate_to: localhost

# Update play network domain and subdomain
- name: set play network domain
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: update
    key: domain
    value: "nlpt.network"
  delegate_to: localhost

# Enable nlpt.online SSO integration
- name: enable SSO login
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: update
    key: nlpt_sso
    value: true
  delegate_to: localhost

# Get integrity timestamp for switchlinks check
- name: get last switchlinks integrity check time
  nils_ost.lpos.setting:
    url: "{{ lpos_url }}"
    session_id: "{{ lpos_session_id }}"
    state: get
    key: integrity_switchlinks
  delegate_to: localhost
"""

RETURN = r"""
key:
    description:
        - The setting key that was queried or updated.
    type: str
    returned: always
    sample: "domain"

value:
    description:
        - The current value of the setting after the operation.
        - For C(state=get), this is the retrieved value.
        - For C(state=update), this is the new value that was set.
    type: raw
    returned: when succeeded
    sample: "nlpt.network"

all_settings:
    description:
        - The full settings dictionary returned from the API (for get state).
        - Contains all setting key-value pairs currently stored in LPOS.
    type: dict
    returned: when state is 'get' and succeeded
    sample: { "domain": "nlpt.network", "subdomain": "onboarding", ... }

updated_key:
    description:
        - The key that was updated (for update state).
    type: str
    returned: when state is 'update' and succeeded
"""


def get_setting(url, session, key):
    """Get all settings via GET /setting/ and return the value for the requested key."""
    response = session.get(url + "setting/")
    if response.status_code >= 400:
        return (False, None, response.text)

    try:
        all_settings = dict()
        for s in response.json():
            all_settings[s["id"]] = s["value"]
    except Exception:
        return (False, None, f"failed to parse JSON response: {response.text}")

    if key not in all_settings:
        return (False, None, f"setting key '{key}' not found")

    return (True, all_settings.get(key), all_settings)


def update_setting(url, session, key, value):
    """Update a single setting via PATCH /setting/{key}/."""
    response = session.patch(url + "setting/" + key + "/", json={"value": value})
    if response.status_code >= 400:
        return (False, None, response.text)

    try:
        result_data = response.json()
    except Exception:
        return (False, None, f"failed to parse JSON response: {response.text}")

    # The API may return the updated value directly or wrapped in a dict
    new_value = (
        result_data.get("value", result_data)
        if isinstance(result_data, dict)
        else result_data
    )
    return (True, new_value, result_data)


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        state=dict(
            type="str",
            required=False,
            choices=["get", "update"],
            default="get",
        ),
        url=dict(type="str", required=True),
        session_id=dict(type="str", required=True, no_log=True),
        key=dict(type="str", required=True),
        value=dict(type="raw", required=False),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        key=None,
        value=None,
        all_settings=None,
        updated_key=None,
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
        state = module.params.get("state", "get")
        key = module.params.get("key")

        if state == "get":
            # --- GET mode ---
            success, value, data_or_error = get_setting(url, session, key)
            if not success:
                module.fail_json(
                    msg=f"failed to get setting '{key}': {data_or_error}",
                    **result,
                )

            result["key"] = key
            result["value"] = value
            result["all_settings"] = data_or_error
            module.exit_json(**result)

        elif state == "update":
            # --- UPDATE mode ---
            if module.params.get("value") is None:
                module.fail_json(
                    msg="value parameter is required when state=update",
                    **result,
                )

            new_value = module.params["value"]

            # First check current value to determine if change is needed
            success, current_value, all_settings = get_setting(url, session, key)
            if not success:
                module.fail_json(
                    msg=f"failed to get setting '{key}': {all_settings}",
                    **result,
                )

            # Check if value actually differs (handle type coercion for bools)
            needs_update = current_value != new_value

            if not needs_update:
                result["key"] = key
                result["value"] = current_value
                result["all_settings"] = all_settings
                module.exit_json(
                    msg=f"setting '{key}' is already as expected",
                    **result,
                )

            # Value differs — perform update
            if module.check_mode:
                result["changed"] = True
                result["key"] = key
                result["value"] = new_value
                result["updated_key"] = key
                module.exit_json(**result)

            success, updated_value, data_or_error = update_setting(
                url,
                session,
                key,
                new_value,
            )
            if not success:
                module.fail_json(
                    msg=f"failed to update setting '{key}': {data_or_error}",
                    **result,
                )

            result["changed"] = True
            result["key"] = key
            result["value"] = updated_value
            result["updated_key"] = key
            module.exit_json(msg=f"updated setting '{key}' to {new_value}", **result)

    except Exception as e:
        module.fail_json(msg=f"Error: {e}", **result)


def main():
    run_module()


if __name__ == "__main__":
    main()

.. _nils_ost.lpos.device_module:


********************
nils_ost.lpos.device
********************

**create or rename a Device**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module manages LPOS Device elements via the LPOS REST API.
- A Device represents a network-connected device detected on a MikroTik switch port.
- Devices are identified by their MAC address (unique, stored without colons) in the LPOS backend.
- The module supports create and update operations.
- When creating or updating, the module searches for an existing device by its MAC address (*mac*) via the LPOS API. If found, it updates the existing record with the provided *desc* with the provided *desc*; otherwise it creates a new one.
- The MAC address is sent to the LPOS backend as part of the create/update payload — the backend enforces uniqueness on this field.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>desc</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">""</div>
                </td>
                <td>
                        <div>Human-readable description (name) of the device. Used to set or rename the device on creation/update</div>
                        <div>When a device is assigned to a seat in LPOS, this field may be auto-set from the Participant&#x27;s name by the backend.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>mac</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>MAC address of the device. Required when <code>state=present</code> or when deleting with <code>state=absent</code>.</div>
                        <div>Must be in hexadecimal format without colons (e.g., <code>112233445566</code>).</div>
                        <div>The LPOS backend enforces uniqueness on this field — no two devices can share the same MAC.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>session_id</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>A valid session ID obtained from a previous login via the <code>login</code> module.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                    <li>absent</li>
                        </ul>
                </td>
                <td>
                        <div>Whether the Device should exist (present) or be removed (absent).</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>url</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The full base URL of the LPOS API endpoint (e.g. <code>http://192.168.0.5:81/api/</code>).</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - The module searches for existing devices by their ``mac`` field. If a device with that MAC already exists, it is updated with the provided *desc*; otherwise a new device is created.
   - No two devices can have the same MAC address.
   - The LPOS backend automatically calculates several fields when certain parameters are set


See Also
--------

.. seealso::

   :ref:`nils_ost.lpos.login_module`
      The official documentation on the **nils_ost.lpos.login** module.
   :ref:`nils_ost.lpos.ippool_module`
      The official documentation on the **nils_ost.lpos.ippool** module.
   :ref:`nils_ost.lpos.table_module`
      The official documentation on the **nils_ost.lpos.table** module.
   :ref:`nils_ost.lpos.switch_module`
      The official documentation on the **nils_ost.lpos.switch** module.


Examples
--------

.. code-block:: yaml

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



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>item</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dict or None</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>the item corresponding to number created, updated or found in LPOS. might be None in case of errors or deletion</div>
                    <br/>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Nils Ost (@nils-ost)

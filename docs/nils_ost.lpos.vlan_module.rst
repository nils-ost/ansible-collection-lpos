.. _nils_ost.lpos.vlan_module:


******************
nils_ost.lpos.vlan
******************

**creates, updates or deletes VLANs on an LPOS instance**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manages VLAN elements on a LanPartyOnboardingSystem (LPOS) instance via its REST API.
- VLANs are used to define network segments for play, management, onboarding, and other purposes.
- A valid session_id from the ``login`` module is required for authentication.



Requirements
------------
The below requirements are needed on the host that executes this module.

- requests


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
                        <div>A human-readable description of the VLAN.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>number</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The VLAN ID (1-1024). Required when <code>state=present</code> or when deleting a specific VLAN with <code>state=absent</code>.</div>
                        <div>Must be unique and not already in use by another VLAN.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>purpose</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>0</li>
                                    <li>1</li>
                                    <li>2</li>
                                    <li><div style="color: blue"><b>3</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>The purpose of the VLAN.</div>
                        <div>Values 0 (play) and 1 (mgmt) must be unique across all VLANs — only one each allowed.</div>
                        <div>Value 2 is for onboarding networks (multiple allowed, one per switch).</div>
                        <div>Value 3 is for other purposes.</div>
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
                        <div>Whether the VLAN should exist (present) or be removed (absent).</div>
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
   - Deleting a VLAN that has associated IpPools or Switch references will fail with an error from the API.
   - When ``state=present`` and ``number`` matches an existing VLAN, the module updates it if any attributes differ.
   - This module requires a valid session cookie passed via the ``session_id``.



Examples
--------

.. code-block:: yaml

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
                    <b>vlan</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>when state is &#x27;present&#x27; and succeeded</td>
                <td>
                            <div>The full VLAN object returned from the API (for present state) or None (for absent).</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;id&#x27;: &#x27;...&#x27;, &#x27;number&#x27;: 10, &#x27;purpose&#x27;: 0, &#x27;desc&#x27;: &#x27;Play network&#x27;}</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>vlan_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>when state is &#x27;present&#x27; and succeeded</td>
                <td>
                            <div>The MongoDB _id of the VLAN element.</div>
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

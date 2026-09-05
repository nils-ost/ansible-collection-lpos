.. _nils_ost.lpos.switch_module:


********************
nils_ost.lpos.switch
********************

**creates, updates or deletes Switches on an LPOS instance**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manages Switch elements on a LanPartyOnboardingSystem (LPOS) instance via its REST API.
- Switches represent MikroTik hardware that the LPOS manages for VLAN and port configuration.
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
                    <b>addr</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>IP address or hostname of the MikroTik switch. Required when <code>state=present</code> or when deleting a specific switch with <code>state=absent</code>.</div>
                        <div>Must be unique — no two switches can share the same address.</div>
                </td>
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
                        <div>A human-readable description of the switch.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>onboarding_vlan_number</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The VLAN number to use as the onboarding VLAN for this switch.</div>
                        <div>Required when <code>purpose</code> is 1 or 2.</div>
                        <div>The module will resolve this VLAN number to its MongoDB _id via the LPOS API before creating/updating the switch.</div>
                        <div>The referenced VLAN must have purpose=2 (onboarding).</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>port_numbering_offset</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">0</div>
                </td>
                <td>
                        <div>Offset added to physical port numbers for display purposes.</div>
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
                                    <li><div style="color: blue"><b>0</b>&nbsp;&larr;</div></li>
                                    <li>1</li>
                                    <li>2</li>
                        </ul>
                </td>
                <td>
                        <div>The purpose of the switch.</div>
                        <div>Value 0 = core switch (no onboarding VLAN required).</div>
                        <div>Values 1 and 2 require an <code>onboarding_vlan_number</code> to be specified.</div>
                        <div>Purpose 1 = participant switch, 2 = mixed switch.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>pw</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">""</div>
                </td>
                <td>
                        <div>password for authenticating to the MikroTik switch.</div>
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
                        <div>Whether the Switch should exist (present) or be removed (absent).</div>
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
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>user</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"admin"</div>
                </td>
                <td>
                        <div>username for authenticating to the MikroTik switch.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - Deleting a switch that has associated Tables will fail with an error from the API.
   - When ``state=present`` and ``addr`` matches an existing switch, the module updates it if any attributes differ.
   - The ``onboarding_vlan_number`` is resolved via the LPOS VLAN API — the VLAN must already exist before this module runs.
   - Switches with purpose 0 (core) automatically have their onboarding VLAN cleared.
   - This module requires a valid session cookie passed via the ``session_id``.



Examples
--------

.. code-block:: yaml

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
                    <b>switch</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>when state is &#x27;present&#x27; and succeeded</td>
                <td>
                            <div>The full Switch object returned from the API (for present state) or None (for absent).</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;id&#x27;: &#x27;...&#x27;, &#x27;addr&#x27;: &#x27;192.168.1.1&#x27;, &#x27;purpose&#x27;: 0, &#x27;desc&#x27;: &#x27;Core switch&#x27;}</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>switch_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>when state is &#x27;present&#x27; and succeeded</td>
                <td>
                            <div>The MongoDB _id of the Switch element.</div>
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

.. _nils_ost.lpos.ippool_module:


********************
nils_ost.lpos.ippool
********************

**create, update or delete an IpPool**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module manages LPOS IpPool elements via the LPOS REST API.
- An IpPool defines a range of IP addresses within a VLAN that can be assigned to devices (seats, additional devices).
- The module supports create, update, and delete operations. For deletion, use ``state=absent`` with the *desc* parameter.
- When creating or updating, the module searches for an existing IpPool by its description (*desc*) field. If found, it updates the existing record; otherwise it creates a new one.
- IP addresses are stored internally as integers. The module accepts IPs in dotted notation (e.g., ``192.168.1.10``) and converts them automatically.
- Each IpPool belongs to exactly one VLAN, referenced by *vlan_number* which is resolved to the VLAN's MongoDB _id.
- The VLAN must already exist before creating an IpPool for it.
- For VLANs with purpose 1 (mgmt) or 2 (onboarding), only ONE IpPool per VLAN is allowed. VLANs with purpose 0 (play) can have multiple IpPools.




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
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Human-readable description of the IP pool. Used as the lookup key to find existing IpPools for update operations.</div>
                        <div>{&#x27;Examples&#x27;: &#x27;<code>table1-play</code>, <code>mgmt-pool</code>, <code>onboarding-range</code>.&#x27;}</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>mask</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">24</div>
                </td>
                <td>
                        <div>CIDR prefix length (subnet mask) for the IP pool.</div>
                        <div>Must be between 8 and 30 inclusive.</div>
                        <div>The mask must encompass both <em>range_start</em> and <em>range_end</em> — all IPs in the range must fall within the same subnet.</div>
                        <div>Default is <code>24</code>, which provides 254 usable addresses (excluding network and broadcast).</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>range_end</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Last IP address of the pool range (end of the assignable IP range).</div>
                        <div>Must be in dotted decimal notation (e.g., <code>192.168.1.50</code>).</div>
                        <div>Must be greater than or equal to <em>range_start</em> and within the subnet defined by <em>mask</em>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>range_start</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>First IP address of the pool range (start of the assignable IP range).</div>
                        <div>Must be in dotted decimal notation (e.g., <code>192.168.1.10</code>).</div>
                        <div>The IP must fall within the subnet defined by <em>mask</em> and cannot overlap with another IpPool on the same VLAN.</div>
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
                        <div>Whether the IpPool should exist (present) or be removed (absent).</div>
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
                    <b>vlan_number</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The VLAN number (not MongoDB _id) of the VLAN this IpPool belongs to.</div>
                        <div>The module resolves this VLAN number to its MongoDB _id via the LPOS VLAN API before creating/updating the IpPool.</div>
                        <div>For play networks (VLAN purpose 0), multiple IpPools can share the same VLAN.</div>
                        <div>For mgmt (purpose 1) and onboarding (purpose 2) VLANs, only one IpPool is allowed per VLAN.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - The module searches for existing IpPools by their ``desc`` field. If multiple pools share the same description, only the first match is updated.
   - The *vlan_number* is resolved via the LPOS VLAN API — the referenced VLAN must already exist before this module runs.
   - Validation error codes. 30 (mask must be between 8 and 30), 31 (mask does not fit range_start and range_end — IPs outside subnet), 32 (range_start must be smaller than or equal to range_end), 33 (IP range overlaps with an existing IpPool), 34 (invalid IP address — out of valid range 01000000 to FFFFFEFD), 39 (only one IpPool allowed for mgmt/onboarding VLANs).
   - Deleting an IpPool that is referenced by a Table will fail with an error from the API.
   - The ``range_start`` and *range_end* IPs are stored as integers internally. The module handles conversion automatically.


See Also
--------

.. seealso::

   :ref:`nils_ost.lpos.login_module`
      The official documentation on the **nils_ost.lpos.login** module.
   :ref:`nils_ost.lpos.vlan_module`
      The official documentation on the **nils_ost.lpos.vlan** module.
   :ref:`nils_ost.lpos.table_module`
      The official documentation on the **nils_ost.lpos.table** module.


Examples
--------

.. code-block:: yaml

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
                            <div>the item corresponding to description created, updated or found in LPOS. might be None in case of errors or deletion</div>
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

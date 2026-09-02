.. _nils_ost.lpos.table_module:


*******************
nils_ost.lpos.table
*******************

**create, update or delete a Table**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module manages LPOS Table elements via the LPOS REST API.
- A Table represents a physical arrangement of seats on MikroTik switch ports. Each table has a unique number, is associated with a specific switch, and defines two IP pools. one for seat devices (play network) and one for additional devices connected to the same table.
- The module supports create, update, and delete operations. For deletion, use ``state=absent`` with the *number* parameter.
- When creating or updating, the module searches for an existing Table by its number (*number*) via the LPOS API. If found, it updates the existing record with the provided parameters; otherwise it creates a new one.
- The switch referenced by *switch* must have purpose 1 (participant) or 2 (mixed). Core switches (purpose 0) cannot host tables.
- Both IP pools (*seat_ip_pool* and *add_ip_pool*) must belong to VLANs with purpose 0 (play/seats).
- The two IP pools must be different — the same pool cannot be used for both seat devices and additional devices on the same table. Additionally, each pool can only serve one role. a pool assigned as ``seat_ip_pool_id`` to one Table cannot be used as ``add_ip_pool_id`` by another Table (and vice versa).
- The module resolves switch descriptions and IP pool descriptions to their MongoDB _ids via the LPOS API before creating/updating the table.




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
                    <b>add_ip_pool</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Description (<em>desc</em> field) of the IpPool used for additional (non-seat) devices on this table.</div>
                        <div>Additional devices are extra devices connected to a table beyond their assigned seat.</div>
                        <div>The referenced IpPool must belong to a VLAN with purpose 0 (play/seats).</div>
                        <div>Once assigned, this pool cannot be used as <em>seat_ip_pool</em> on any other table.</div>
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
                        <div>Human-readable description of the table. Used to set or rename the table on creation/update.</div>
                        <div>{&#x27;Examples&#x27;: &#x27;<code>Table 1</code>, <code>Stage A</code>, <code>Room B-Row3</code>.&#x27;}</div>
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
                        <div>Unique table number. Used as the primary identifier for lookup and must be unique across all tables in LPOS.</div>
                        <div>Must be greater than or equal to 0.</div>
                        <div>Required when <code>state=present</code> or when deleting with <code>state=absent</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>seat_ip_pool</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Description (<em>desc</em> field) of the IpPool used for seat devices on this table.</div>
                        <div>The referenced IpPool must belong to a VLAN with purpose 0 (play/seats).</div>
                        <div>This pool defines the IP range assigned to each seat. <code>ip = range_start + seat_number - 1</code>.</div>
                        <div>Once assigned, this pool cannot be used as <em>add_ip_pool</em> on any other table.</div>
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
                        <div>Whether the Table should exist (present) or be removed (absent).</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>switch</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Description (<em>desc</em> field) of the Switch that provides ports for this table.</div>
                        <div>The referenced switch must have <em>purpose</em> set to 1 (participant) or 2 (mixed). Core switches (purpose 0) cannot host tables.</div>
                        <div>The module resolves this description to the switch&#x27;s MongoDB _id via the LPOS Switch API.</div>
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
   - The module searches for existing tables by their ``number`` field. If a table with that number already exists, it is updated with the provided parameters; otherwise a new table is created.
   - Both *seat_ip_pool* and *add_ip_pool* must be different — using the same pool for both will fail validation.
   - Each IP pool can only serve one role across all tables. a pool assigned as ``seat_ip_pool_id`` to one table cannot be used as ``add_ip_pool_id`` on another, and vice versa.
   - The *switch*, *seat_ip_pool*, and *add_ip_pool* parameters are resolved via the LPOS API — these resources must already exist before this module runs.
   - Validation error codes. 40 (number must be >= 0), 41 (FK not found — switch, seat_ip_pool, or add_ip_pool does not exist), 42 (switch purpose must be 1 or 2, not 0/core), 43 (IP pool VLAN purpose must be 0/play), 44 (seat_ip_pool already in use as add_ip_pool on another table), 45 (both pools cannot be the same), 46 (add_ip_pool already in use as seat_ip_pool on another table).
   - Deleting a table that has associated Seats will fail with an error from the API.


See Also
--------

.. seealso::

   :ref:`nils_ost.lpos.login_module`
      The official documentation on the **nils_ost.lpos.login** module.
   :ref:`nils_ost.lpos.switch_module`
      The official documentation on the **nils_ost.lpos.switch** module.
   :ref:`nils_ost.lpos.ippool_module`
      The official documentation on the **nils_ost.lpos.ippool** module.
   :ref:`nils_ost.lpos.seat_module`
      The official documentation on the **nils_ost.lpos.seat** module.


Examples
--------

.. code-block:: yaml

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

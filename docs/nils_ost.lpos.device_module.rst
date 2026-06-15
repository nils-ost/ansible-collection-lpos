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
- This module is intended to create or rename LPOS Devices




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
                        <div>name (description) of Device</div>
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
                        <div>MAC-Address of Device</div>
                        <div>used as primary identifier in this module</div>
                        <div>in hex without colons (e.g. 112233445566)</div>
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
                        <div>the session-id used for authentication on API-Endpoint</div>
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
                        <div>the full URL of API-Endpoint</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: create device
      nils_ost.lpos.device:
        url: "{{ lpos.url }}"
        session_id: "{{ lpos.session_id }}"
        mac: 112233445566
      delegate_to: localhost
      register: device1

    - name: name device
      nils_ost.lpos.device:
        url: "{{ lpos.url }}"
        session_id: "{{ lpos.session_id }}"
        mac: 112233445566
        name: some device
      delegate_to: localhost
      register: device1

    - name: rename device
      nils_ost.lpos.device:
        url: "{{ lpos.url }}"
        session_id: "{{ lpos.session_id }}"
        mac: 112233445566
        name: some important device
      delegate_to: localhost
      register: device1



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

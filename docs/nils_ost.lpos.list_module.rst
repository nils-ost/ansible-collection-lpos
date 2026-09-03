.. _nils_ost.lpos.list_module:


******************
nils_ost.lpos.list
******************

**returns a list of all LPOS elements of a given kind**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module retrieves a list of all existing elements of a specified kind from the LPOS REST API.
- The LPOS backend exposes element lists via plain GET requests to ``GET /api/{element}/``.
- Supported element types are ``vlan``, ``ippool``, ``switch``, ``table``, ``seat``, ``participant``, ``device``, and ``port``.
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
                    <b>element</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>vlan</li>
                                    <li>ippool</li>
                                    <li>switch</li>
                                    <li>table</li>
                                    <li>seat</li>
                                    <li>participant</li>
                                    <li>device</li>
                                    <li>port</li>
                        </ul>
                </td>
                <td>
                        <div>The element kind to list.</div>
                        <div>Supported values are <code>vlan</code>, <code>ippool</code>, <code>switch</code>, <code>table</code>, <code>seat</code>, <code>participant</code>, <code>device</code>, and <code>port</code>.</div>
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




Examples
--------

.. code-block:: yaml

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
                    <b>count</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The number of elements returned in the list.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>items</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>A list of all element objects of the requested kind returned from the LPOS API.</div>
                            <div>Each item is a dictionary containing the element&#x27;s attributes as returned by the backend.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;id&#x27;: &#x27;507f1f77bcf86cd799439011&#x27;, &#x27;number&#x27;: 10, &#x27;purpose&#x27;: 0, &#x27;desc&#x27;: &#x27;Play network&#x27;}, {&#x27;id&#x27;: &#x27;507f1f77bcf86cd799439012&#x27;, &#x27;number&#x27;: 20, &#x27;purpose&#x27;: 2, &#x27;desc&#x27;: &#x27;Onboarding&#x27;}]</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Nils Ost (@nils-ost)

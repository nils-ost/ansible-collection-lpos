.. _nils_ost.lpos.setting_module:


*********************
nils_ost.lpos.setting
*********************

**get or update LPOS system settings**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manages LPOS system settings via the LPOS REST API at ``/setting/``.
- Settings are key-value pairs that control various aspects of the LPOS system including network configuration, SSO integration, metrics, and VLAN defaults.
- A valid session_id from the ``login`` module is required for authentication.
- All settings are readable by any authenticated user. Only settings listed in the backend's ``_admin_writeable`` list can be modified, and only by admin users.




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
                    <b>key</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The setting key to get or update.</div>
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
                                    <li><div style="color: blue"><b>get</b>&nbsp;&larr;</div></li>
                                    <li>update</li>
                        </ul>
                </td>
                <td>
                        <div>Whether to retrieve a setting (<code>get</code>) or update it (<code>update</code>).</div>
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
                    <b>value</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">raw</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The new value to set when <code>state=update</code>.</div>
                        <div>Type depends on the setting key.</div>
                        <div>For IP-type settings, pass an integer representing the IP address (use dotted-to-int conversion).</div>
                        <div>For bool settings, use Python-style booleans (true/false in YAML).</div>
                        <div>For int settings, pass a plain integer.</div>
                        <div>For str settings, pass a string.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - Only admin users can modify settings listed in the backend's ``_admin_writeable`` list. Non-admin users will receive an authorization error when attempting to update restricted keys.
   - IP-type settings (``play_ip``, ``play_dhcp``, etc.) are stored as integers internally. When updating, pass the integer representation of the IP address.
   - Integrity timestamp settings and cached management interface settings (``lpos_mgmt_mac``, ``lpos_mgmt_ip``) are read-only — they are managed by the backend.
   - The module uses a PATCH request to update a single setting key-value pair at ``/setting/{key}/``.


See Also
--------

.. seealso::

   :ref:`nils_ost.lpos.login_module`
      The official documentation on the **nils_ost.lpos.login** module.


Examples
--------

.. code-block:: yaml

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
                    <b>all_settings</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>when state is &#x27;get&#x27; and succeeded</td>
                <td>
                            <div>The full settings dictionary returned from the API (for get state).</div>
                            <div>Contains all setting key-value pairs currently stored in LPOS.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;domain&#x27;: &#x27;nlpt.network&#x27;, &#x27;subdomain&#x27;: &#x27;onboarding&#x27;, &#x27;...&#x27;: None}</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>key</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The setting key that was queried or updated.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">domain</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>updated_key</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>when state is &#x27;update&#x27; and succeeded</td>
                <td>
                            <div>The key that was updated (for update state).</div>
                    <br/>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>value</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">raw</span>
                    </div>
                </td>
                <td>when succeeded</td>
                <td>
                            <div>The current value of the setting after the operation.</div>
                            <div>For <code>state=get</code>, this is the retrieved value.</div>
                            <div>For <code>state=update</code>, this is the new value that was set.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">nlpt.network</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Nils Ost (@nils-ost)

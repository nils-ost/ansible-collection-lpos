# nils_ost.lpos.basic_config

**configures the most of basics to run LanPartyOnboardingSystem**

Version added: 1.0.0

- [Synopsis](#synopsis)
- [Role Variables](#role-variables)

## Synopsis

A role for configuring most of the basic settings needed to run an instance of LanPartyOnboardingSystem

VLANs, Switches, IpPools and Tables can be created, updated and deleted. Settings can be updated and named Devices can be created. requires already running LPOS (e.g. through role `nils_ost.lpos.install_with_docker`)

## Role Variables

| Variable      | Type | Default  | Comment                                             |
| ------------- | ---- | -------- | --------------------------------------------------- |
| lpos_admin_pw | str  | password | password to be set for the initial admin account    |
| lpos_api_port | str  | 80       | LPOS port used for API login                        |
| lpos_api_path | str  | /api/    | LPOS API path used for login                        |
| lpos_settings | dict | {}       | Settings to be configured (see below for structure) |
| lpos_vlans    | dict | {}       | VLANs to be configured (see below for structure)    |
| lpos_switches | dict | {}       | Switches to be configured (see below for structure) |
| lpos_ippools  | dict | {}       | IpPools to be configured (see below for structure)  |
| lpos_tables   | dict | {}       | Tables to be configured (see below for structure)   |
| lpos_devices  | dict | {}       | Devices to be configured (see below for structure)  |

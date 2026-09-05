# nils_ost.lpos.basic_config

**configures most of the basics to run LanPartyOnboardingSystem**

Version added: 1.0.0

- [Synopsis](#synopsis)
- [Role Variables](#role-variables)
  - [Structure of: lpos\_settings](#structure-of-lpos_settings)
  - [Structure of: lpos\_vlans](#structure-of-lpos_vlans)
  - [Structure of: lpos\_switches](#structure-of-lpos_switches)
  - [Structure of: lpos\_ippools](#structure-of-lpos_ippools)
  - [Structure of: lpos\_tables](#structure-of-lpos_tables)
  - [Structure of: lpos\_devices](#structure-of-lpos_devices)
- [Full Example](#full-example)

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

### Structure of: lpos_settings

It's a simple dict where the key defines the Setting (-name) to be updated and the value is the value to be set.  
Values can be of any type the API requires for the corresponding Setting.

### Structure of: lpos_vlans

It's a dict of dicts, where the key of the top-level dictionary defines the VLAN number.
The second-level (or value of the top-level dict) sets some variables for this VLAN.

The possible variables on second-level are:

| Variable | Type | Required | Default | Comment                                                 |
| -------- | ---- | -------- | ------- | ------------------------------------------------------- |
| purpose  | int  | false    | 3       | one of: 0 (play), 1 (mgmt), 2 (onboarding) or 3 (other) |
| desc     | str  | false    | ""      | description for VLAN                                    |

### Structure of: lpos_switches

It's a dict of dicts, where the key of the top-level dictionary defines the address (addr) for a Switch.
The second-level (or value of the top-level dict) sets some variables for this Switch.

The possible variables on second-level are:

| Variable               | Type | Required | Default | Comment                                                              |
| ---------------------- | ---- | -------- | ------- | -------------------------------------------------------------------- |
| purpose                | int  | false    | 0       | one of: 0 (core), 1 (participant) or 2 (mixed)                       |
| onboarding_vlan_number | int  | partial  |         | vlan-number to be used for onboarding (required on purpose: 1 and 2) |
| desc                   | str  | false    | ""      | description for Switch                                               |
| user                   | str  | false    | admin   | username to be used for connecting to the Switch                     |
| pw                     | str  | false    | ""      | description for VLAN                                                 |

> [!NOTE]
> `onboarding_vlan_number` is internally resolved to the corresponding id

### Structure of: lpos_ippools

It's a dict of dicts, where the key of the top-level dictionary defines the description for an IpPool.
The second-level (or value of the top-level dict) sets some variables for this IpPool.

The possible variables on second-level are:

| Variable    | Type | Required | Default | Comment                                                     |
| ----------- | ---- | -------- | ------- | ----------------------------------------------------------- |
| range_start | str  | true     |         | First IP address of the pool range                          |
| range_end   | str  | true     |         | Last IP address of the pool range                           |
| mask        | int  | false    | 24      | CIDR prefix length (subnet mask) for the IP pool            |
| vlan_number | int  | true     |         | The VLAN number (not id) of the VLAN this IpPool belongs to |

> [!NOTE]
> `vlan_number` is internally resolved to the corresponding id

### Structure of: lpos_tables

It's a dict of dicts, where the key of the top-level dictionary defines the Table number.
The second-level (or value of the top-level dict) sets some variables for this Table.

The possible variables on second-level are:

| Variable     | Type | Required | Default | Comment                                                                                 |
| ------------ | ---- | -------- | ------- | --------------------------------------------------------------------------------------- |
| desc         | str  | false    | ""      | description for Table                                                                   |
| switch       | str  | true     |         | Description (not id) of the Switch that provides ports for this Table                   |
| seat_ip_pool | str  | true     |         | Description (not id) of the IpPool used for seat devices on this Table                  |
| add_ip_pool  | str  | true     |         | Description (not id) of the IpPool used for additional (non-seat) devices on this Table |

> [!NOTE]
> `switch` `seat_ip_pool` and `add_ip_pool` are internally resolved to their corresponding ids

### Structure of: lpos_devices

It's a dict of dicts, where the key of the top-level dictionary defines the MAC Address of Device (without colons).
The second-level (or value of the top-level dict) sets some variables for this Device.

The possible variables on second-level are:

| Variable     | Type | Required | Default | Comment                |
| ------------ | ---- | -------- | ------- | ---------------------- |
| desc         | str  | false    | ""      | description for Device |

## Full Example

```yaml
---
lpos_api_port: 8000
lpos_api_path: "/"

lpos_settings:
  play_ip: 3232267012
  domain: local.domain
  absolute_seatnumbers: true

lpos_vlans:
  12:
    purpose: 0
    desc: "play network"
  13:
    purpose: 1
    desc: "mgmt network"
  21:
    purpose: 2
    desc: "Participants1 Onboarding"

lpos_switches:
  127.0.0.1:1337:
    purpose: 0
    desc: "C1"
  127.0.0.1:1338:
    purpose: 2
    onboarding_vlan_number: 21
    desc: "P1"

lpos_ippools:
  mgmt-pool:
    range_start: 10.13.66.1
    range_end: 10.13.66.99
    mask: 24
    vlan_number: 13
  play-t1-pool:
    range_start: 192.168.123.10
    range_end: 192.168.123.19
    mask: 24
    vlan_number: 12
  play-addi-pool:
    range_start: 192.168.123.50
    range_end: 192.168.123.99
    mask: 24
    vlan_number: 12
  onboarding-p1-pool:
    range_start: 172.16.2.10
    range_end: 172.16.2.100
    mask: 24
    vlan_number: 21

lpos_tables:
  1:
    desc: Table 1
    seat_ip_pool: play-t1-pool
    add_ip_pool: play-addi-pool
    switch: P1

lpos_devices:
  aabbccddeeaa:
    desc: modem
  aabbccddeebb:
    desc: server1
  aabbccddeecc:
    desc: server2
```

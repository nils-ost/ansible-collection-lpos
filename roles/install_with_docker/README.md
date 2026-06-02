# nils_ost.lpos.install_with_docker

**installs LPOS within docker**

Version added: 1.0.0

- [Synopsis](#synopsis)
- [Role Variables](#role-variables)
- [Example](#example)

## Synopsis

A role for installing LanPartyOnboardingSystem as docker containers with the help of compose

This role mainly just creates the compose directory, places the compose-file and executes `docker compose up`.
It requires docker to be already installed on target system, including the compose plugin.
You might want to take a look at [geerlingguy.docker](https://github.com/geerlingguy/ansible-role-docker) to install docker on your system.

## Role Variables

| Variable          | Type | Default       | Comment                                                         |
| ----------------- | ---- | ------------- | --------------------------------------------------------------- |
| lpos_timezone     | str  | Europe/Berlin | timezone to be set for containers                               |
| lpos_compose_dir  | str  | /opt/lpos     | location where compose-file and volume directorys are created   |
| lpos_release      | str  | latest        | container image version tag to be used in compose-file          |
| lpos_auto_upgrade | bool | false         | whether container images are updated on role run or not         |
| lpos_admin_pw     | str  | password      | password to be set for the initial admin account                |

> [!NOTE]
> only on the initial run (a fresh installation) `lpos_admin_pw` sets the admin password.  
> subseqent changes of this variable do NOT affect the accounts, that might be present in the database of LPOS.

## Example

`group_vars/lpos.yml`

```yaml
---
lpos_compose_dir: "/opt/services/lpos"
lpos_release: v1.0.0
lpos_admin_pw: someSecre7
```

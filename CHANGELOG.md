# nils_ost LPOS Collection Release Notes

**Topics**

- <a href="#v1-1-0">v1\.1\.0</a>
  - <a href="#release-summary">Release Summary</a>
  - <a href="#minor-changes">Minor Changes</a>
- <a href="#v1-0-0">v1\.0\.0</a>
  - <a href="#release-summary-1">Release Summary</a>
  - <a href="#new-modules">New Modules</a>
  - <a href="#new-roles">New Roles</a>

<a id="v1-1-0"></a>

## v1\.1\.0

<a id="release-summary"></a>

### Release Summary

expanded device configuration options

<a id="minor-changes"></a>

### Minor Changes

- added commit_config parameter to module device
- added retreat_config parameter to module device
- updated role basic_config to be able to utilize commit_config and retreat_config

<a id="v1-0-0"></a>

## v1\.0\.0

<a id="release-summary-1"></a>

### Release Summary

Initial release of nils_ost\.lpos collection with 8 modules and 2 roles

<a id="new-modules"></a>

### New Modules

- nils_ost\.lpos\.device \- create or rename a Device\.
- nils_ost\.lpos\.ippool \- create\, update or delete an IpPool\.
- nils_ost\.lpos\.list \- returns a list of all LPOS elements of a given kind\.
- nils_ost\.lpos\.login \- creates authenticated session\, to be used by further modules\.
- nils_ost\.lpos\.setting \- get or update LPOS system settings\.
- nils_ost\.lpos\.switch \- creates\, updates or deletes Switches on an LPOS instance\.
- nils_ost\.lpos\.table \- create\, update or delete a Table\.
- nils_ost\.lpos\.vlan \- creates\, updates or deletes VLANs on an LPOS instance\.

<a id="new-roles"></a>

### New Roles

- nils_ost\.lpos\.basic_config \- installs LPOS within docker\.
- nils_ost\.lpos\.install_with_docker \- installs LPOS within docker\.

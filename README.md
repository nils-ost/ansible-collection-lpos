# Ansible Collection - nils_ost.lpos

This repository contains the `nils_ost.lpos` Ansible Collection. For install and configure a instance of [LanPartyOnboardingSystem](https://github.com/nils-ost/LanPartyOnboardingSystem)

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.13.9**.

For collections that support Ansible 2.9, please ensure you update your `network_os` to use the
fully qualified collection name (for example, `cisco.ios.ios`).
Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## External requirements

Currently only the `requests` Python library is required by this collection, to be able to run the modules.
As this collection is intended to do it's module call `delegate_to: localhost` it's enough to `pip install requests` locally.

## Included content

<!--start collection content-->
### Modules
Name | Description
--- | ---
[nils_ost.lpos.login](https://github.com/nils-ost/ansible-collection-lpos/blob/main/docs/nils_ost.lpos.login_module.rst)|creates authenticated session, to be used by further modules

<!--end collection content-->

### Roles

Name | Description
--- | ---
[nils_ost.lpos.install_with_docker](https://github.com/nils-ost/ansible-collection-lpos/blob/main/roles/install_with_docker/README.md)|installs LanPartyOnboardingSystem within docker

## Using this collection

```bash
ansible-galaxy collection install nils_ost.lpos
```

You can also include it in a `requirements.yml` file and install it via
`ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
  - name: nils_ost.lpos
```

To upgrade the collection to the latest available version, run the following
command:

```bash
ansible-galaxy collection install nils_ost.lpos --upgrade
```

You can also install a specific version of the collection, for example, if you
need to downgrade when something is broken in the latest version (please report
an issue in this repository). Use the following syntax where `X.Y.Z` can be any
[available version](https://galaxy.ansible.com/nils_ost/lpos):

```bash
ansible-galaxy collection install nils_ost.lpos:==X.Y.Z
```

See
[Ansible Using Collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)
for more details.

## Release notes

See the
[changelog](CHANGELOG.md).

## Roadmap

This collection is mainly intended to be used by myself. Therefor I'm just developing the stuff I need for my current projects on a irregular basis.
But if you find some benefit in this collection, feel free to use it. If you like to have some features added feel free to create a pull-request
or write an issue with a feature-request and I'm going to see if I can make it happen.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](LICENSE) to see the full text.

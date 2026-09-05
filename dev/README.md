# some notes for myself on developing this module

## dev-env setup

```
sudo apt update; sudo apt install -y python3 virtualenv direnv
virtualenv -p /usr/bin/python3 venv
venv/bin/pip install -r requirements.txt
venv/bin/pip install -r dev/requirements.txt
venv/bin/pre-commit install
sed -nr '/direnv hook bash/!p;$aeval "\$(direnv hook bash)"' -i ~/.bashrc
source ~/.bashrc
echo -e "source venv/bin/activate\nunset PS1" > .envrc
direnv allow
```

## writing changelogs (fragements)

[Guide on how to write Changelog Fragments](https://docs.ansible.com/projects/ansible/devel/community/development_process.html#changelogs-how-to)

[List of available Changelog Fragement Categories](https://github.com/ansible-community/antsibull-changelog/blob/main/docs/changelogs.md#changelog-fragment-categories)

Linting the written fragments

```
antsibull-changelog lint
```

## local testing (within collection)

```
ansible-galaxy collection build --force
ansible-galaxy collection install --force nils_ost-lpos-1.0.0.tar.gz
ansible-playbook test/test_basic_config.yml
```

## local testing (in another project)

  * build collection `rm *.tar.gz; ansible-galaxy collection build`
  * `cd` to your local testing project and "pull in" the collection (this ensures the correct environment for this project is used)
    * `ansible-galaxy collection install --force ~/workspace/ansible-collection-lpos/nils_ost-lpos-1.0.0.tar.gz`

## doing a release

  * set release-version in `galaxy.yml`
  * create changelog fragement in `changelogs/fragments` with release-version, that contains at least `release_summary` (see example below)
  * generate changelog `antsibull-changelog release`
  * commit everything
  * build collection `rm *.tar.gz; ansible-galaxy collection build`
  * publish collection `ansible-galaxy collection publish nils_ost-lpos-1.0.0.tar.gz --token `
  * tag the commit with release-version (e.g. `v1.0.0`)
  * push to github `git push origin main; git push origin --tags`
  * create release on GitHub

### changelog fragement for version 1.0.0

`changelogs/fragments/v1.0.0.yml`

```
release_summary: |
  This is the first proper release of ``nils_ost.lpos`` collection on 2026-06-01.
  The added Modules and Role were just carried over from other local projects.
```

## setup to push to ansible-galaxy

In the default ansible config the `token_path` points to `~/.ansible/galaxy_token`, therefore just put the galaxy token of the namespace inside this file, and everything is ready to be pushed.

The full documentation about building and distributing a collection can be found here: [Ansible Collection Distributing](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections_distributing.html)

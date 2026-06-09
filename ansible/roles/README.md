# Ansible roles

Each `ansible/roles/<name>/` directory is a standard [Ansible role](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html):

```
ansible/roles/my_helper/
├── tasks/main.yml           the role's tasks (typical entry point)
├── defaults/main.yml        default variables
├── handlers/main.yml        handlers
└── meta/main.yml            role metadata; galaxy_info.description shows in the catalog
```

Local roles are installed to the user's Ansible roles directory at `source add` time and are usable from any range-config thereafter — they don't need to be referenced from a blueprint in this source. When a blueprint *does* reference one, use the directory name (`my_helper`) under `roles:` in `range-config.yml`. If a local role shares a name with a galaxy role declared in a blueprint's `requirements.yml`, Ludus installs the local role and skips the galaxy fetch for that name.

For collections shipped alongside roles, see [`../collections/`](../collections/README.md). Galaxy roles and collections a blueprint pulls in from *outside* the bundle are declared in that blueprint's `requirements.yml` — see [`blueprints/`](../../blueprints/README.md).

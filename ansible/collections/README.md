# Ansible collections

Each `ansible/collections/<dir>/` directory is a standard [Ansible collection](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_structure.html) — a directory with a `galaxy.yml` at its root:

```
ansible/collections/my_collection/
├── galaxy.yml               namespace, name, version, description (REQUIRED)
├── roles/                   roles in the collection
├── plugins/                 modules / plugins
└── README.md
```

Ludus reads `galaxy.yml` for the collection's FQCN (`<namespace>.<name>`) and installs the directory to `<collections-path>/ansible_collections/<namespace>/<name>/` at `source add` time — per-user by default, or instance-wide with `--global-roles`. The `galaxy.yml` `description` shows in the catalog and picker.

Reference a collection's content from a blueprint the normal way — a 3-part FQCN role (`namespace.collection.role`) under `roles:` in `range-config.yml`. If a blueprint's `requirements.yml` also declares a collection this source ships, Ludus installs the bundled copy and skips the galaxy fetch for that FQCN, so the shipped version wins.

Any of these subdirectories may itself be a **git submodule** (see the repo README's Submodules note); it is pulled at `source add`.

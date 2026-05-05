# Ludus Source Template

A Ludus source is a versioned bundle of Packer templates, Ansible roles, and blueprints, served from a git repo, tarball, or local directory. `ludus source add` registers the contents in one step.

This repo is a starting point for publishing your own source. Click **Use this template**, edit the files, push, then run:

```bash
ludus source add https://github.com/<you>/<repo>
ludus blueprint apply <repo>/example   # if your source ships a blueprint
ludus range deploy
```

Any git host works (GitHub, GitLab, self-hosted). You can also pass `source add` a local tarball (`source add ./source.tar.gz`) or a local directory (`source add -d ./my-source`). Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

## What you can ship

A source can carry any combination of three artifact types. All three are optional, but a source must ship at least one.

| Artifact         | Where it goes                                                                                  | Visibility                                                          |
|------------------|------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Blueprints       | `blueprints/<id>/`                                                                             | Per-source, addressed as `<sourceID>/<id>`                          |
| Packer templates | `templates/<n>/` (shared) or `blueprints/<id>/templates/<n>/` (per-blueprint)                  | Global registry by name                                             |
| Ansible roles    | `roles/<n>/` (shared) or `blueprints/<id>/roles/<n>/` (per-blueprint)                          | User-scoped by default; `--global-roles` for instance-wide          |

A blueprints-only source, a roles-only source, and a templates-only source are all valid.

## Layout in this template

```
LICENSE                              MIT placeholder; replace with your own
source.yml                           repo metadata: name, authors, homepage, license
scripts/validate.py                  manifest schema check; extend with your own rules
.github/workflows/validate.yml       GitHub Actions: runs scripts/validate.py on every push
.gitlab-ci.yml                       GitLab CI: runs scripts/validate.py on every push

blueprints/example/                  one blueprint
├── blueprint.yml                    display metadata
├── range-config.yml                 the range config
├── requirements.yml                 pinned galaxy roles, off-galaxy roles
├── subscription_refs.yml            license-gated role names (delete if unused)
├── roles/                           Ansible roles only this blueprint uses
└── templates/                       Packer templates only this blueprint uses

roles/                               Ansible roles shared across blueprints in this source
templates/                           Packer templates shared across blueprints in this source
```

The empty `roles/` and `templates/` directories are tracked with `.gitkeep` so the structure ships with the template. Drop a role or template in (or delete the directories you don't need).

## Galaxy and git roles

Plain galaxy roles like `geerlingguy.docker` need no `requirements.yml`; just list them under `roles:` in `range-config.yml`. Use `requirements.yml` to pin a version or pull from GitHub/GitLab:

```yaml
# blueprints/<id>/requirements.yml
roles:
  - name: geerlingguy.docker
    version: 7.4.4                                  # pin a galaxy role
  - name: badsectorlabs.ludus_adcs                  # off-galaxy: name + src
    src: https://github.com/badsectorlabs/ludus_adcs
    version: v1.2.0
```

Names must match what `roles:` in `range-config.yml` references; otherwise Ludus installs one role and tries to use another.

## Subscription roles

If your blueprint references roles from the Ludus subscription catalog (Enterprise / private roles), declare them in `blueprints/<id>/subscription_refs.yml`:

```yaml
roles:
  - ludus_ghosts_client
  - ludus_adcs
```

The bytes of subscription roles never travel in the bundle; only their names. At apply time Ludus reads this file and returns `403` with the unmet roles when the target instance has no valid license or the catalog doesn't cover one of them. Plain galaxy roles and local roles do NOT belong here.

## Custom Packer templates

Each `templates/<name>/` directory is a standard Ludus Packer template, the same shape as the [Ludus template catalog](https://gitlab.com/badsectorlabs/ludus/-/tree/main/templates):

```
templates/my-debian-base/
├── my-debian-base.pkr.hcl   the Packer build config
├── http/                    Linux: preseed.cfg / kickstart served at install time
└── Autounattend.xml         Windows only: unattended install answer file
```

Templates register to a global, single-namespace pool. If two sources both register a template named `my-debian-base`, the second `source add` will conflict. Prefix shared template names with your source slug (`bsl-debian-base`, not `debian-base`).

After `ludus source add`, run `ludus templates build` to produce the VM image.

## Custom Ansible roles

Each `roles/<name>/` directory is a standard [Ansible role](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html):

```
roles/my_helper/
├── tasks/main.yml           the role's tasks (typical entry point)
├── defaults/main.yml        default variables
├── handlers/main.yml        handlers
└── meta/main.yml            role metadata, dependencies
```

Reference the role by directory name (`my_helper`) under `roles:` in `range-config.yml`. If a local role shares a name with a galaxy role, Ludus skips the galaxy install and uses the local role.

## Required fields

The validator and the server enforce these:

- `source.yml`: `manifest_version`. Everything else is optional. The whole file is optional too.
- `blueprint.yml` (when you ship a blueprint): `manifest_version`, `id`, `name`, `description`, `version` (semver), `config`. Optional: `tags`, `thumbnail`, `min_ludus_version`.

License, homepage, and authors live in `source.yml` and apply to every blueprint in the source.

The example files are annotated inline.

## Versioning

Two separate fields:

- `manifest_version` is the schema version of the manifest file. Ludus bumps it when the format changes incompatibly. Leave it at `1`.
- `version` is your semver for the blueprint. Bump it any time you change a blueprint and want users to see it as new. Push to your repo, then users run:

```bash
ludus source sync <repo>             # pull latest manifests + reinstall any new role deps
ludus blueprint info <repo>/example  # see the new version
ludus blueprint apply <repo>/example # write the new config to their range
ludus range deploy                   # rebuild
```

`ludus blueprint apply` always writes whatever's currently in the source; there's no automatic upgrade prompt. The `version` field is for display and changelog purposes; pin to a git tag (`source update <repo> --ref v1.2.0`) to lock users to a specific release.

## More

Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

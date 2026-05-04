# Ludus Source Template

A Ludus source is a versioned bundle of Packer templates, Ansible roles, and blueprints packaged in a specific layout. Like a container image, one URL ships everything Ludus needs; `ludus source add` registers it in a single step.

This repo is a starting point for publishing your own. Click **Use this template**, edit the files below, push, then run:

```bash
ludus source add https://github.com/<you>/<repo>
ludus blueprint apply <repo>/example
ludus range deploy
```

Any git host works (GitHub, GitLab, self-hosted). You can also feed `source add` a local tarball/zip (`source add ./source.tar.gz`) or a local directory (`source add -d ./my-source`). Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

## What you can ship

A source can carry any combination of three artifact types. You don't have to ship all of them.

| Artifact | Where it goes | Visibility |
|----------|---------------|------------|
| **Blueprints** (range configs) | `blueprints/<id>/` | Per-source, addressed as `<sourceID>/<id>` |
| **Packer templates** (custom OS images) | `templates/<n>/` (shared) or `blueprints/<id>/templates/<n>/` (per-blueprint) | Global registry by name |
| **Ansible roles** (local) | `roles/<n>/` (shared) or `blueprints/<id>/roles/<n>/` (per-blueprint) | User-scoped by default; `--global-roles` for instance-wide |

A blueprints-only source, a roles-only source, and a templates-only source are all valid.

## Files in this template

```
LICENSE                           MIT placeholder; replace with your own
source.yml                        repo metadata: name, authors, homepage, license
blueprints/example/
  blueprint.yml                   one blueprint's display metadata
  range-config.yml                the range config; same shape `ludus range config get` returns
scripts/validate.py               manifest schema check; extend with your own rules
.github/workflows/validate.yml    runs scripts/validate.py on every push
```

Add when you need them:

```
blueprints/<id>/requirements.yml  pinned versions, or roles hosted off galaxy.ansible.com
blueprints/<id>/templates/<n>/    custom OS image (Packer config) only this blueprint uses
blueprints/<id>/roles/<n>/        local Ansible role only this blueprint uses
templates/<n>/                    custom OS image shared across blueprints in this source
roles/<n>/                        local Ansible role shared across blueprints in this source
```

## Galaxy and git roles

Plain galaxy roles like `geerlingguy.docker` need no `requirements.yml`; just list them under `roles:` in `range-config.yml`. Reach for `requirements.yml` only when you need to pin a version or pull from GitHub/GitLab:

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

## Custom Packer templates

Each `templates/<name>/` directory is a standard Ludus Packer template, the same shape as the [Ludus template catalog](https://gitlab.com/badsectorlabs/ludus/-/tree/main/templates):

```
templates/my-debian-base/
  my-debian-base.pkr.hcl   the Packer build config
  http/                    Linux: preseed.cfg / kickstart served at install time
  Autounattend.xml         Windows only: unattended install answer file
```

Templates register to a global, single-namespace pool. If two sources both register a template named `my-debian-base`, the second `source add` will conflict. Prefix shared template names with your source slug to avoid collisions (`bsl-debian-base`, not `debian-base`).

After `ludus source add`, run `ludus templates build` to produce the actual VM image.

## Custom Ansible roles

Each `roles/<name>/` directory is a standard [Ansible role](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html):

```
roles/my_helper/
  tasks/main.yml           the role's tasks (typical entry point)
  defaults/main.yml        optional: default variables
  handlers/main.yml        optional: handlers
  meta/main.yml            optional: role metadata, dependencies
```

Reference the role by directory name (`my_helper`) under `roles:` in `range-config.yml`. If a local role shares a name with a galaxy role, Ludus skips the galaxy install entirely and only the local role gets installed.

## Required fields

The validator and the server enforce these:

- **`source.yml`**: `manifest_version`. Everything else is optional. The whole file is optional too.
- **`blueprint.yml`**: `manifest_version`, `id`, `name`, `description`, `version` (semver), `config`. Optional: `tags`, `thumbnail`, `min_ludus_version`.

License, homepage, and authors live in `source.yml` and apply to every blueprint published in the source.

The example files have these annotated inline.

## Versioning

Two separate fields:

- **`manifest_version`** is the schema version of the manifest file. Ludus bumps it when the format changes incompatibly. Leave it at `1`.
- **`version`** is *your* semver for the blueprint. Bump it any time you change a blueprint and want users to see it as new. Push to your repo, then users run:

```bash
ludus source sync <repo>           # pull latest manifests + reinstall any new role deps
ludus blueprint info <repo>/example # see the new version
ludus blueprint apply <repo>/example # write the new config to their range
ludus range deploy                  # rebuild
```

`ludus blueprint apply` always writes whatever's currently in the source; there's no automatic upgrade prompt. The `version` field is for display and changelog purposes; pin to a git tag (`source update <repo> --ref v1.2.0`) to lock users to a specific release.

## More

Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

# Ludus Source Template

A Ludus source is a versioned bundle of Packer templates, Ansible roles, and blueprints, served from a git repo, tarball, or local directory. `ludus source add` registers the contents in one step.

This repo is a starting point for publishing your own source. Use it as a template (or clone it and repoint `origin` at your new repo), edit the files, push, then run:

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
| Packer templates | `templates/<n>/` at source root                                                                | Global registry by name                                             |
| Ansible roles    | `roles/<n>/` at source root                                                                    | User-scoped by default; `--global-roles` for instance-wide          |

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
└── requirements.yml                 galaxy roles, collections, subscription roles

roles/                               Ansible roles shipped by this source
templates/                           Packer templates shipped by this source
```

The empty `roles/` and `templates/` directories are tracked with `.gitkeep` so the structure ships with the template. Drop a role or template in (or delete the directories you don't need).

`scripts/validate.py` and the two CI workflows ship a basic manifest check out of the box — it confirms your `blueprint.yml` parses and references resolve. If your org has its own CI conventions, delete `scripts/` and `.github/workflows/validate.yml` (and/or `.gitlab-ci.yml`) and wire in your own; nothing else in the template depends on them.

## Role and collection dependencies

`blueprints/<id>/requirements.yml` is the single manifest for everything a blueprint needs from outside the bundle. Every role referenced under `roles:` in `range-config.yml` must be declared here (or shipped locally under `roles/`); Ludus surfaces an undeclared-dependency warning at sync time otherwise.

Three sections, all optional:

```yaml
roles:
  - name: geerlingguy.docker
    version: 7.4.4                                  # pin a galaxy role
  - name: badsectorlabs.ludus_adcs                  # off-galaxy: name + src
    src: https://github.com/badsectorlabs/ludus_adcs
    version: v1.2.0

collections:
  - name: community.crypto                          # required when range-config
    version: 2.16.0                                 # references a FQCN role
                                                    # like community.crypto.openssl_certificate

subscription_roles:
  - ludus_ghosts_client                             # license-gated role; bare scalar
  - name: ludus_adcs                                # or structured shape
```

A few rules worth knowing:

- **Names must match** what `range-config.yml` references; otherwise Ludus installs one role and tries to run another.
- **Collections are required for FQCN role refs.** A 3-part reference like `namespace.collection.role` won't work unless `namespace.collection` is listed under `collections:`.
- **Subscription roles never travel in the bundle** — only their names. At apply time Ludus serves them from the license catalog. If the target instance has no valid license, or the catalog doesn't cover one of the names, the apply returns `403`. Version pinning isn't currently supported for subscription roles — whatever the catalog reports as current gets installed.
- **Local roles win over galaxy.** If a `roles/<name>/` directory exists in the bundle (per-blueprint or at source root), it satisfies the dependency without a galaxy lookup.

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

Local roles are installed to the user's Ansible roles directory at `source add` time and are usable from any range-config thereafter — they don't need to be referenced from a blueprint in this source. When a blueprint *does* reference one, use the directory name (`my_helper`) under `roles:` in `range-config.yml`. If a local role shares a name with a galaxy role, Ludus skips the galaxy install and uses the local role.

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

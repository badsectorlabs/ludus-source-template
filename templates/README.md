# Packer templates

Each `templates/<name>/` directory is a standard Ludus Packer template, the same shape as the templates in the [Bad Sector Labs source](https://github.com/badsectorlabs/ludus-source-bsl/tree/main/templates):

```
templates/my-debian-base/
├── my-debian-base.pkr.hcl   the Packer build config
├── template.yml             optional: manifest_version + a catalog description
├── http/                    Linux: preseed.cfg / kickstart served at install time
└── Autounattend.xml         Windows only: unattended install answer file
```

`template.yml` is optional — Packer templates carry no native description, so it supplies one for the catalog (`ludus source list`):

```yaml
manifest_version: 1
description: Debian 12 (Bookworm) minimal x64 server.
```

Templates install into each installing user's own Packer directory — so they survive Ludus server updates — and are keyed by the template's `*-template` name (the `vm_name` in the `.pkr.hcl`, not the folder name). A name that matches an already-installed or built-in template is skipped rather than overwritten, so prefix names you expect to share with your source slug (`bsl-debian-base`, not `debian-base`).

After `ludus source add`, run `ludus templates build` to produce the VM image.

## Required fields

`template.yml` is optional, but when present it must declare `manifest_version` (leave it at `1`). `description` is an optional one-line summary shown in the catalog.

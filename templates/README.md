# Packer templates

Each `templates/<name>/` directory is a standard Ludus Packer template, the same shape as the templates in the [Bad Sector Labs source](https://github.com/badsectorlabs/ludus-source-bsl/tree/main/templates):

```
templates/my-debian-base/
├── my-debian-base.pkr.hcl   the Packer build config (incl. `description` + `thumbnail_path` variables)
├── thumbnail.png            optional: the catalog icon referenced by the thumbnail_path variable
├── http/                    Linux: preseed.cfg / kickstart served at install time
└── Autounattend.xml         Windows only: unattended install answer file
```

Templates install into each installing user's own Packer directory — so they survive Ludus server updates — and are keyed by the template's `*-template` name (the `vm_name` in the `.pkr.hcl`, not the folder name). A name that matches an already-installed or built-in template is skipped rather than overwritten, so prefix names you expect to share with your source slug (`bsl-debian-base`, not `debian-base`).

After `ludus source add`, run `ludus templates build` to produce the VM image.

## Catalog metadata

Give the template a catalog description and icon (shown by `ludus source list` and the GUI) with two static variables in the `.pkr.hcl`, so all of a template's metadata lives in one file:

```hcl
variable "description" {
  type    = string
  default = "Debian 12 (Bookworm) minimal x64 server."
}

variable "thumbnail_path" {
  type    = string
  default = "thumbnail.png"
}
```

Packer requires a variable's `default` to be a literal, so both stay plain static strings — unlike `template_description`, which is a build-time `local` (it carries an `isotime` stamp and is the Proxmox template's own notes, not a catalog blurb).

`thumbnail_path` is a **relative path** to an image bundled in the template dir. Ludus stores it on the template's record; the GUI shows it on template cards, falling back to a built-in OS glyph when absent. Use a **square, transparent PNG** (256×256 works well) and keep it legible small — it renders as little as 24px. Raster only (PNG/JPEG/GIF/WebP); SVG is not accepted.

## template.yml (optional)

A template needs no `template.yml` at all — the metadata above lives in the packer file. For backward compatibility a `template.yml` is still honored as a fallback for both fields:

```yaml
description: Debian 12 (Bookworm) minimal x64 server.
thumbnail: thumbnail.png
```

`manifest_version` is optional — Ludus defaults it to 1, and you only need to set it once a future breaking schema requires it.

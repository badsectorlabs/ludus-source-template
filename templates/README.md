# Packer templates

Each `templates/<name>/` directory is a standard Ludus Packer template, the same shape as the templates in the [Bad Sector Labs source](https://github.com/badsectorlabs/ludus-source-bsl/tree/main/templates):

```
templates/my-debian-base/
├── my-debian-base.pkr.hcl   the Packer build config (incl. `description` + `icon_path` variables)
├── icon.png            optional: the catalog icon referenced by the icon_path variable
├── http/                    Linux: preseed.cfg / kickstart served at install time
└── Autounattend.xml         Windows only: unattended install answer file
```

Templates install into each installing user's own Packer directory and are keyed by the template's `*-template` name (the `vm_name` in the `.pkr.hcl`, not the folder name). A name that matches an already-installed or built-in template is skipped rather than overwritten, so prefix names you expect to share with your source slug (`bsl-debian-base`, not `debian-base`).

After `ludus source add`, run `ludus templates build` to produce the VM image.

## Catalog metadata

Give the template a catalog description and icon (shown by `ludus source list` and the GUI) with two static variables in the `.pkr.hcl`:

```hcl
variable "description" {
  type    = string
  default = "Debian 12 (Bookworm) minimal x64 server."
}

variable "icon_path" {
  type    = string
  default = "icon.png"
}
```


`icon_path` is a **relative path** to an image bundled in the template dir. The Ludus GUI shows it on template cards, falling back to a built-in OS glyph when absent. Use a **square, transparent PNG** (256×256 works well) and ensure its legibility as small sizes (24px at the smallest). Raster only (PNG/JPEG/GIF/WebP); SVG is not accepted.

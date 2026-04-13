## Inno Setup 6 Graphics — What's Supported

With `WizardStyle=modern`, Inno Setup supports three distinct graphic slots. Your script already uses two of them but is missing `WizardSmallImageFile`, and the `[Code]` section's custom page adds no visual value as written. Here's the full picture:

| Directive | Where it appears | Format | Notes |
|---|---|---|---|
| `SetupIconFile` | The Setup.exe file icon itself | `.ico` | Multi-res ICO recommended |
| `WizardImageFile` | Left sidebar on Welcome & Finish pages | `.png` or `.bmp` | Tall portrait image |
| `WizardSmallImageFile` | Top-right corner on all inner pages | `.png` or `.bmp` | Small square |
| `UninstallDisplayIcon` | Windows Add/Remove Programs list | `.ico` | Already handled via `{app}\AbCS.ico` |

PNG with transparency is fine for all bitmap slots in IS6.

---

Here is the modified script with `WizardSmallImageFile` added and all graphics renamed to the `name_WxH` convention. The pointless custom welcome page in `[Code]` is also removed since the standard Welcome page with your sidebar image already handles branding:
## Graphics files to create

| Filename | Dimensions | Format | Used for |
|---|---|---|---|
| `graphics\abcs_wizard_164x314.png` | 164 × 314 px | PNG | Left sidebar on Welcome & Finish pages — your main branding moment; teal/green open book + soundwave fits well here |
| `graphics\abcs_small_55x55.png` | 55 × 55 px | PNG | Top-right corner on all inner pages (directory, options, progress, etc.) — icon-style treatment of your logo |
| `graphics\abcs_icon_256x256.ico` | Multi-res ICO: 16, 32, 48, 256 px | ICO | Embedded into Setup.exe itself; also used for taskbar and title bar during install |
| `graphics\AbCS.ico` | Same multi-res ICO | ICO | Already exists — installed to `{app}` for shortcuts |

**Two things removed from your original:**

1. The `[Code]` section — the `CreateCustomPage` call was producing a plain-text overlay on the standard Welcome page with no actual graphic, which adds noise without benefit. The `WizardImageFile` sidebar covers that role properly.
2. The `[CustomMessages]` `WelcomeTitle/Line` entries — these were only used by the now-removed custom page.
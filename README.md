# Liquid Glass

A jade-glass theme for [Omarchy](https://omarchy.org/).

Most Omarchy themes are a palette. This one is a *material*: the palette is
only half of it, and the other half is Hyprland's blur, a set of layer rules,
and per-app background alpha working together so that windows, the bar, the
launcher and notifications all read as translucent panes lit from the same
direction.

![Liquid Glass](backgrounds/1-omarchy-liquid-glass.png)

## Install

```bash
omarchy theme install https://github.com/Jitheswar/omarchy-liquid-glass-theme.git
```

Or clone it into place and switch manually:

```bash
git clone https://github.com/Jitheswar/omarchy-liquid-glass-theme.git ~/.config/omarchy/themes/liquid-glass
omarchy theme set "Liquid Glass"
```

## The palette

Every colour was sampled out of `backgrounds/1-omarchy-liquid-glass.png`
rather than picked by eye, so the desktop and the wallpaper share one light
source.

| Role | Colour | |
|---|---|---|
| `background` | `#070E0C` | the deepest point of the wallpaper, between the ribbons |
| `foreground` | `#D6E4DE` | cool off-white with a green cast |
| `accent` | `#6BCCA9` | the mint glow rimming the glass pill |
| `cursor` | `#A8E4D3` | the specular hit where light catches a curved edge |
| `color8` | `#4B7265` | the wallpaper's mid grey-green, for muted text |

The red and violet slots (`color1`, `color5`) are deliberately kept off-jade.
Syntax highlighting collapses into mush if every hue sits inside the same
150–180° wedge, so those two carry the contrast the wallpaper doesn't.

## How the glass is built

**Transparency comes from the app, not the compositor.** Each terminal sets its
own background alpha (`0.84`) while leaving glyphs fully opaque. Lowering
window opacity in Hyprland instead would fade the text along with the
background, which is why `active_opacity` stays at `1.0` here.

**Blur is what turns transparency into glass.** Four passes at size 7, with
`vibrancy` at `0.35` to put back the saturation a plain gaussian blur washes
out — the difference between glass and fog. A little `noise` hides the banding
that four passes would otherwise expose across the wallpaper's wide gradients.

**Corners are squircles.** `rounding_power = 3.0` gives continuous curvature
rather than a circular arc, which is most of what makes an edge look moulded
instead of cut.

**Shell surfaces are layers, not windows**, so they need their own rules —
`layerrule = blur on` per namespace, plus `ignore_alpha` so the transparent
margin around a floating panel doesn't get blurred along with the panel.

`xray` is off on purpose: seeing other windows blurred behind the front one is
the layered depth the theme is built around. Turn it on in `hyprland.conf` to
trade that for lower GPU load.

## What's in here

| File | |
|---|---|
| `colors.toml` | drives everything Omarchy generates (btop, helix, obsidian, gum, chromium, hyprlock…) |
| `hyprland.conf` | blur, squircle rounding, specular borders, shadows, layer rules |
| `waybar.css` | floating frosted bar with a lit rim |
| `walker.css` | frosted launcher |
| `swayosd.css`, `mako.ini` | frosted OSD and notifications |
| `alacritty.toml`, `ghostty.conf`, `kitty.conf`, `foot.ini` | full palette + background alpha |
| `neovim.lua` | aether.nvim fed this exact palette, transparent background |
| `hyprlock.conf` | translucent lock field over the blurred wallpaper |
| `backgrounds/` | three wallpapers |

Each of those files carries a comment explaining *why* it overrides Omarchy's
generated template — worth reading before changing one.

## Tuning

Turn the effect down if it's heavy on your GPU, in `hyprland.conf`:

```ini
decoration:blur:passes = 2      # from 4
decoration:blur:xray   = true   # blur only the wallpaper, not windows behind
```

Or make the panes clearer/foggier by changing `opacity` in `alacritty.toml`,
`background-opacity` in `ghostty.conf`, `background_opacity` in `kitty.conf`,
and `alpha` in `foot.ini`.

## Wallpapers

`1-omarchy-liquid-glass.png` is the default. The other two are generated from
SVG (`2-liquid-meniscus`, `3-liquid-submerged`) and are there so
`omarchy theme bg next` has somewhere to go — swap them for your own freely.

## Notes

- Icons use `Yaru-prussiangreen-dark`, which ships with Omarchy.
- VS Code points at **Ocean Green: Dark** (`jovejonovski.ocean-green`), the
  closest jade theme on the marketplace; Omarchy installs it on first switch.
- Neovim needs `bjarneo/aether.nvim`, which LazyVim will fetch on next start.

## Licence

MIT. The wallpapers are included under the same terms.

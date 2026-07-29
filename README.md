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

The target is clear, lit glass — not frost. Those are opposite settings, and
it's worth being explicit about why, because the obvious knobs push the wrong
way. **Frost is diffusion**: many blur passes plus grain, tuned to *hide* what
sits behind. This aims at something you look *through*.

**Blur is kept low.** Size 4, three passes. At size 8 and four passes you get a
fogged panel; down here the shapes behind stay legible, which is what makes the
pane read as transparent rather than merely tinted. This is the single biggest
difference from a frosted theme.

**Grain is switched off.** `noise = 0.003`, near Hyprland's floor. Grain is
exactly what the eye reads as "frosted" — it is the texture of etched glass.
Just enough is left to stop the wallpaper's wide gradients from banding.

**The glass is lit, not veiled.** `brightness = 1.18` lifts the pane off the
wallpaper so it looks illuminated instead of smeared, and `vibrancy = 0.80`
puts back the saturation a plain gaussian washes out, so colour bleeds through
as refraction rather than grey.

**The edge does most of the work.** A 3px border with a 90° gradient — near
white at the top falling to near black at the base — reads as a bevel catching
a single overhead light. At 1px it collapses into a plain outline. In the GTK
surfaces the same idea is an `inset 0 1px 0` highlight plus a vertical
gradient body; remove that one inset shadow and the bar goes flat instantly.

**Transparency comes from the app, not the compositor.** Each terminal sets its
own background alpha (`0.74`) while leaving glyphs fully opaque. Lowering
window opacity in Hyprland instead would fade the text along with the
background, which is why `active_opacity` stays at `1.0`.

**Corners are squircles.** `rounding = 20` (Hyprland's ceiling) at
`rounding_power = 4.5` gives continuous curvature rather than a circular arc
pasted onto a straight edge — most of what makes a corner look moulded.

**Shell surfaces are layers, not windows**, so they need their own rules —
`layerrule = blur on` per namespace, plus `ignore_alpha` so the clear margin
around a floating panel doesn't get blurred along with the panel.

`xray` is off on purpose: seeing other windows refracted behind the front one
is the layered depth the theme is built around. Turn it on in `hyprland.conf`
to trade that for lower GPU load.

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

Lighter on the GPU, in `hyprland.conf`:

```ini
decoration:blur:passes = 2      # from 3
decoration:blur:xray   = true   # blur only the wallpaper, not windows behind
```

Want it frosted instead of clear? Push the two settings that define the
difference:

```ini
decoration:blur:size  = 8       # from 4
decoration:blur:noise = 0.02    # from 0.003 — grain is what reads as "frosted"
```

Clearer or more solid panes: `opacity` in `alacritty.toml`,
`background-opacity` in `ghostty.conf`, `background_opacity` in `kitty.conf`,
`alpha` in `foot.ini`. Below about `0.65` text starts to fight the wallpaper.

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

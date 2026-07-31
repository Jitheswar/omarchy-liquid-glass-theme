# Liquid Glass

A glass theme for [Omarchy](https://omarchy.org/).

Most Omarchy themes are a palette. This one is a *material*, and the surfaces
have no colour at all. The bar, launcher, OSD, notifications, lock field and
window borders are built from white and black at low alpha and nothing else —
so they take their colour from whatever is behind them. Over a green wallpaper
the desktop is green; over a blue one it is blue; over a photograph it is
whatever the photograph is. Nothing needs retuning per wallpaper, because
there is nothing tinted to tune.

That is what glass actually does, and it is the one thing a tinted theme
cannot fake. The rest is Hyprland's blur, a set of layer rules and per-app
background alpha, working together so every surface reads as a translucent
pane lit from the same direction.

There is no theme colour left anywhere, including the palette. The only hues
that survive are the ANSI 16, and only because `ls` needs a directory to look
different from a file and `git diff` needs an addition to look different from a
deletion. Those are readings, not decoration.

![Liquid Glass](backgrounds/1-omarchy-liquid-glass.png)

## Requirements

**Hyprland 0.56.0 or newer.** Five things set that floor, and all of them fail
loudly rather than degrading, so it is worth checking before installing:

| Feature | Needs | Why |
|---|---|---|
| `decoration:rounding_power = 4.5` | 0.47.0 | squircle corners — added as "supercircular window corners" ([#8943](https://github.com/hyprwm/Hyprland/pull/8943)) |
| `windowrule`/`layerrule … match:…` | 0.53.0 | the rule syntax was rewritten and the old comma form removed ([#12269](https://github.com/hyprwm/Hyprland/pull/12269)) |
| `decoration:glow` | 0.55.0 | the inner rim itself — "add glow decoration" ([#13862](https://github.com/hyprwm/Hyprland/pull/13862)) |
| …with a gradient | 0.56.0 | the rim is lit from one direction, which needs the gradient form ([#15208](https://github.com/hyprwm/Hyprland/pull/15208)) |
| `decoration:shadow` with a gradient | 0.56.0 | same, for shadows ([#14809](https://github.com/hyprwm/Hyprland/pull/14809)) |
| `decoration:motion_blur` | 0.56.0 | added as "a motion blur option to windows" ([#14911](https://github.com/hyprwm/Hyprland/pull/14911)) |

0.56.0 is the binding one. On 0.55 the glow block loads but its gradient does
not, and `motion_blur` is unknown; below 0.53.0 every `windowrule` and
`layerrule` is a config error too — which means no blur on the bar, launcher,
notifications or OSD, and no window transparency. The theme would load as a
palette and nothing else. Check with `hyprctl version`.

Recent Omarchy 3.x ships 0.56.0. Earlier 3.x releases do not, so the version
of Omarchy is not on its own the thing to check — `hyprctl version` is.
Developed and verified against Hyprland 0.56.0 / Omarchy 3.8.4.

Nothing else is required. No plugin, no patched compositor, no `hyprpm`, no
package outside what Omarchy already installs — clone it, set it, and every
effect described below is running. That is a constraint the theme is built
under rather than a happy accident, and the section on what it costs is
[further down](#what-a-plugin-would-add-and-why-there-isnt-one).

### Verified

- **Fractional and mixed scaling.** Checked on a second output at `scale
  1.5` alongside the built-in panel at `1.0`. The bar renders correctly at
  both — 1px rim intact, radius correct, blur working, no seams or doubled
  edges. Compositor cost was unchanged within measurement noise when the
  second output was added.
- **Multi-GPU.** This machine has Intel and NVIDIA adapters; Hyprland renders
  on the Intel one. Nothing here is GPU-specific, but the theme has not been
  tested with the compositor driven from a discrete GPU.
- **Not verified: two *physical* monitors.** Only one physical display was
  available, so the second output above was a virtual one. Multi-monitor
  frame time is therefore untested, as is anything involving differing
  refresh rates. No GPU profiler was installed, so the load figure above is
  compositor CPU time, not GPU frame time.
- **Terminal legibility.** Unchanged, and measured rather than assumed:
  glyph-to-background contrast across an Alacritty window at `alpha = 0.74`
  has a median of 14.6:1, against 14.9:1 for the same colours fully opaque.
  Terminals only make the *background* translucent, so the glyphs never
  thin out. All four terminal configs are untouched by any of the above.
- **The inner rim.** Swept and measured on a throwaway virtual output, so no
  part of a real session is in any of the figures: falloff profile at four
  range/power pairs, active against inactive, and the fullscreen exemption
  forced with an opaque colour to make its absence unambiguous. The numbers
  are in `hyprland.conf` beside the settings they justify.
- **Not verified: motion blur.** It is a function of per-frame displacement,
  so a screenshot caught mid-animation misses it and slowing the animation
  down far enough to catch one removes the displacement being rendered. Both
  were tried. What is verified is that it loads, that it engages only during
  a move or resize, and that it costs nothing at rest — not what the smear
  looks like. One line in [Tuning](#tuning) turns it off.

## Install

```bash
omarchy theme install https://github.com/Jitheswar/omarchy-liquid-glass-theme.git
```

That is the whole install for the bar. Earlier versions of this file told you
to set `"height": 38` in `~/.config/waybar/config.jsonc`, and **if you followed
that, put it back to 26**:

```jsonc
"height": 26,   // Omarchy's default
```

The instruction was wrong twice over. waybar's `height` is a floor rather than
a height, and this bar clears it either way — it is as tall as its contents
demand, which on the shipped font is 45px whether config.jsonc says 26 or 38.
So it changed nothing here. What it *did* change was a file Omarchy owns and
the theme does not, where 38 survived switching away and left every other
theme — all of them drawn for the stock 26 — with a bar twelve pixels too tall
and no clue why.

Nothing replaces it. The measurements are in `waybar.css` beside the margin
that actually does the work.

Then round the lock field, which a theme cannot reach either. Change this one
line inside the `input-field { }` block of `~/.config/hypr/hyprlock.conf`:

```ini
rounding = 22   # Omarchy ships 0
```

That is `radius-lg`, the same step the OSD uses — the field is 650x100, the
same order of size. It takes effect the next time you lock; nothing to
restart.

**Known limitation:** the shipped theme alone cannot round the lock field.
Omarchy's `hyprlock.conf` `source`s the theme's file and then writes its own
`input-field { }` block, and hyprlock registers `input-field` as an
anonymous-key-based category — so a second block from a theme adds a *second*
password field rather than overriding the first. A theme is limited to
substituting the five colour variables into that shared base config. The other
two shape properties in the same position, `shadow_passes` and
`outline_thickness`, are documented with suggested values at the top of
`hyprlock.conf`.

Then take the colour out of `fastfetch`, which is the third and last thing a
theme cannot reach. In `~/.config/fastfetch/config.jsonc`, the logo carries
`"color": { "1": "green" }` and the module rows carry `"keyColor"` in green,
blue and magenta — 21 of them. Every one becomes:

```jsonc
"default"
```

That is not "make it grey". `default` emits `ESC[39m`, the terminal's *own*
foreground — which, with the harmoniser installed, is the one colour in the
theme that already tracks the wallpaper. So the logo and every key end up the
same tinted off-white as the rest of your text, and follow the wallpaper from
then on with nothing further to run. A one-time edit that stays dynamic.

Nothing is lost by it. fastfetch already emits `ESC[1m` for keys regardless of
colour, so the key/value distinction was being carried by **weight** before any
of those hues were applied — the colour was decoration layered on a difference
that already existed. Which is the same argument, and the same fix, as the
green that used to sit on the battery in `waybar.css`. The percentage readings
inside the rows keep their colour, because those are readings.

**Why the theme cannot just ship this:** `config.jsonc` is Omarchy's file, not
the theme's, and Omarchy rewrites it. `palette/harmonize.py` could be made to
patch it on every wallpaper change, and deliberately is not — the harmoniser
can be stopped from *writing* under another theme, but nothing would revert
what it had already written, so switching to Tokyo Night would leave Tokyo
Night wearing this theme's tint. A theme that leaks colour into another theme's
session is a worse bug than a green logo.

### What this theme leaves behind when you switch away

A theme should be removable by switching away from it. This is the full
inventory of what Liquid Glass touches outside its own directory, audited
rather than remembered, because two of these used to be real bugs — a bar
twelve pixels too tall on every other theme, and every GTK4 app on the machine
left translucent.

**Reverts itself. Nothing to do.**

| | why |
|---|---|
| The palette, and every terminal config | `omarchy-theme-set` rebuilds `current/theme` from scratch on each switch |
| Icon *setting* (`icons.theme`) | `omarchy-theme-set-gnome` re-reads it per theme, falling back to `Yaru-blue` |
| Browser tint, VSCode, keyboard LEDs | Omarchy re-runs its own setter for each on every switch |
| `~/.config/gtk-4.0/gtk.css` | an `@import` that silently no-ops once the theme is gone — see above |
| Bar height | the theme no longer asks for one; it never needed to |

**Left installed, but inert.**

| | |
|---|---|
| `~/.local/share/icons/LiquidGlass/` | an unreferenced icon directory once gsettings points elsewhere, like any installed icon theme. `rm -rf` it if you want the disk back |
| `liquid-glass-harmonize.path` / `.service` | still enabled, and the first thing the script does is read `current/theme.name` and `exit 0` unless this theme is active. `systemctl --user disable --now liquid-glass-harmonize.path` removes it |

**Un-applies itself on the way out.**

| File | While active | On switching away |
|---|---|---|
| `~/.config/hypr/hyprlock.conf` | `rounding = 22` | back to Omarchy's `0` |
| `~/.config/fastfetch/config.jsonc` | `"default"` ×22 | the original file, verbatim |

These two live in files Omarchy owns rather than in the theme — hyprlock
because a theme may only substitute variables into Omarchy's shared
`input-field` block, fastfetch because `config.jsonc` is Omarchy's. They used
to be manual edits that followed you to the next theme. `hooks/liquid-glass`,
installed by `./install` into `~/.config/omarchy/hooks/theme-set.d/`, now
handles both: Omarchy runs everything in that directory on *every* theme
change and passes the new theme's name, which is the only moment a theme is
told it is being switched away from.

Two rules it will not break, both of them tested:

- **It restores rather than guesses.** Mapping `"default"` back to
  green/blue/magenta is not invertible — three colours went in, one came out —
  so the original is copied aside on the way in and put back byte-for-byte on
  the way out. A full round trip `diff`s clean.
- **It will not touch what is not ours.** A `rounding` you set yourself is left
  alone in both directions, and a backup is discarded rather than restored if
  the file stopped looking like the one the hook wrote — so an
  `omarchy refresh` in between is safe.

### Removing the theme

`./uninstall` is the clean path and takes effect immediately. Removing the
theme through **Omarchy menu → Style → Remove theme** also works, but not at
the moment you click it, and the difference is worth knowing:
`omarchy-theme-remove` does nothing but `rm -rf` the theme directory. It does
not switch themes and it fires no hook, so there is no moment for anything to
run. Your desktop also keeps working, because `current/theme` still holds the
copy Omarchy built.

The cleanup happens at **the next theme change**, which in practice is your
very next action — the theme you pick to replace it. The hook finds its own
directory gone, and treats that as removal rather than a switch: it reverts
hyprlock and fastfetch, removes the gtk.css shim, the icons, the harmoniser
units and its state directory, and finally deletes itself. A theme that has
been deleted should not keep running code on every switch forever.

Verified end to end with the theme directory absent — hyprlock back to
`rounding = 0`, shim gone, icons gone, units gone, state gone, hook
self-removed.

So both routes end in the same place. The only window where anything is left
behind is *removed the theme and then never set another one*, and in that
window `current/theme` still holds the full copy, so nothing looks broken
either.

`palette/harmonize.py` still does not patch either file, and that has not
changed with the hook. The harmoniser runs on *wallpaper* changes, which is the
wrong moment: it is never told a theme is being switched away from, so anything
it wrote would have no matching revert. That is what the hook is for.

### The rest of the install

```bash
~/.config/omarchy/themes/liquid-glass/install
```

That is everything `omarchy theme set` cannot do, in one command. Safe to run
again — every step is idempotent, and re-running is how you pick up new icons
after a `git pull`. `./uninstall` reverses all of it.

It does three things, described below: points GTK at the theme's `gtk.css`,
installs the folder icons, and installs a hook that applies and **un**-applies
the two settings living in files Omarchy owns. Nothing here is optional in
practice — the glass folder icons need the first two to work at all, which is
why they stopped being a list of commands to copy by hand.

#### What it does

**`gtk.css` — translucent GTK4 windows.** Omarchy applies no theme `gtk.css`
at all, so GTK gets a two-line file pointing at the theme's:

```bash
printf '@import url("../omarchy/current/theme/gtk.css");\n' > ~/.config/gtk-4.0/gtk.css
```

Without it the glass folder icons cannot work. They carry no colour and take
the colour of whatever is behind them, which inside a file manager is the file
manager's own opaque background — so they render grey no matter what the
wallpaper is. Log out and back in, or restart the app.

**This is an `@import`, not a copy, and that is the point.** Earlier versions
copied the file, which had no way to stop applying: Omarchy rewrites
`current/theme` on every switch and no other theme ships a `gtk.css`, so the
copy went on making every GTK4 app on the machine 25% translucent under themes
never designed for it. The import simply fails when the file is not there,
which turns "the next theme has no gtk.css" from the objection into the
mechanism. Measured on gnome-calculator's window body:

| | window body |
|---|---|
| shim, current theme ships no `gtk.css` | **54.9** — opaque, reverted |
| old copied file, same situation | 37.6 — still translucent |
| shim, current theme ships this file | 37.5 — identical to the copy |

The path is relative to `~/.config/gtk-4.0/`, so it resolves for any user with
no editing. **If you copied the old file, overwrite it with the line above** —
that is the whole migration.

**`icons/` — the glass folders.** See `icons/README.md`; it is a `cp -r` and a
`gtk-update-icon-cache`. `icons.theme` already points GNOME at the result, so
the icons appear as soon as the directory exists.

### Manual install

Or clone it into place and switch manually:

```bash
git clone https://github.com/Jitheswar/omarchy-liquid-glass-theme.git ~/.config/omarchy/themes/liquid-glass
omarchy theme set "Liquid Glass"
```

## The palette

Neutral. Everything structural — background, foreground, cursor, accent,
selection and all four greys — is a grey, so nothing in this file tints the
desktop.

| Role | Colour | |
|---|---|---|
| `background` | `#0A0A0A` | near-black, no cast |
| `foreground` | `#E0E0E0` | plain off-white |
| `accent` | `#FFFFFF` | emphasis is brightness now, not hue |
| `cursor` | `#FFFFFF` | |
| `color8` | `#6E6E6E` | muted text |

The ANSI 16 keep their hues, and that is not a hedge. `color2` is what `ls`
paints a directory and what `git diff` paints an addition; `color1` is what it
paints a deletion. Greying those out would not remove theme colour, it would
remove the ability to tell one thing from another. They are spread deliberately
wide, because syntax collapses into mush if every hue sits in the same wedge —
the green and cyan simply lost the mint cast they used to carry.

## Harmonising the palette with the wallpaper

Optional, and off unless you install it.

The surfaces have no colour, so they take the wallpaper's. Anything carrying its
own palette could not: the terminals' sixteen hues are fixed, and so is the
browser's chrome and the editor's syntax. On the magenta wallpaper that meant
green directory names on a magenta field, and a browser still tinted with the
theme's old jade. This is the one place "switching wallpaper switches the theme"
was only ever true of the shell.

`palette/harmonize.py` closes that. It is a **rotation, not an extraction** —
the distinction matters. Palette-from-image tools replace the sixteen colours
with whatever the picture contains, which loses both properties the palette
exists for: `git diff` needs deletions red and additions green, and the sixteen
need to stay far enough apart that syntax does not collapse. Instead every
colour keeps its own hue and is pulled at most 12° toward the wallpaper's, in
OKLCh, with lightness and chroma held exactly.

Two things follow by construction rather than by measurement:

- **Contrast cannot change.** Contrast is a function of lightness; lightness is
  what is held. Measured drift across all six wallpapers: 0.12 on ratios that
  run 5:1 to 15:1.
- **No colour crosses into another's name.** 12° is not a taste call — the
  palette's tightest pair is blue and cyan at 26° apart, and the bound comes
  from sweeping every wallpaper to find where the wheel starts folding. At 30°
  red lands on orange; at 20° yellow starts reading as olive.

`palette/test_harmonize.py` asserts both against every shipped wallpaper, so
raising the bound cannot quietly ruin one wallpaper while looking fine on
another.

The effect is meant to be felt rather than noticed. On the magenta wallpaper
green moves 147° → 135° and cyan 203° → 215° — still plainly green, still
plainly cyan, but now lit from the same direction as everything else.

### The text itself

Rotating the sixteen was aimed at the wrong text. Those are the hues `ls` and a
syntax highlighter reach for; almost everything else on a terminal screen is
drawn in `foreground`, and that stayed a flat neutral grey sitting on a
wallpaper-lit pane. A 12° rotation on colours that make up a fraction of the
screen was never going to make a terminal read as part of the desktop.

So the foreground takes the wallpaper's hue too, at a fixed low chroma with its
lightness held exactly — `TEXT_CHROMA` in `harmonize.py`. On the magenta
wallpaper `#E0E0E0` becomes `#EBDCDF`.

This is the cheapest tint in the file, and the reason is worth stating: **a
neutral has no name to cross into.** The entire 12° bound above exists because
green can stop looking green and that costs a reading. Off-white cannot stop
looking off-white, so the only thing worth protecting is contrast — and holding
lightness protects it by construction. Measured 14.998 before, 14.93 after, on
a scale where that difference is quantisation.

It is the one neutral that moves. Background, cursor, accent, the selection
pair and the ANSI greys stay hueless; they are the glass, and glass has no
colour of its own. `test_harmonize.py` asserts both halves of that.

### What it covers

| | |
|---|---|
| the four terminals | full palette, live — no reopening |
| `chromium.theme` | the browser's chrome, pushed as a managed policy and signalled to running browsers |
| `neovim.lua` | the editor's palette, on next `nvim` start |

The browser is the interesting one, and it is the exception the theme's
two-camps rule already predicts. Terminals stay neutral because at alpha 0.74
the wallpaper is genuinely behind them, so the hue arrives through the glass.
Chromium draws opaque and exposes no transparency setting, so a neutral seed
there is just grey — the tint has to be **baked in**. It is held at exactly the
lightness of `#0A0A0A` so the browser stays as dark as every other surface, and
given the wallpaper's hue at the chroma the old jade seed used, so the strength
of the tint is the one the theme already shipped and only its hue is new.

`neovim.lua` is rewritten by substituting its palette hexes, not by templating
it. aether takes a colour table *and* an `on_highlights` function, and
generating the whole file would mean this quietly owning a hand-maintained one
— every later edit to `neovim.lua` would have to be mirrored or be silently
dropped whenever harmonising is on. The test asserts the substitution changes
no line count and leaves the greys alone.

**Not covered:** `helix.toml` and `obsidian.css` are generated by Omarchy from
`colors.toml` at theme-set time, so following the wallpaper would mean
reimplementing Omarchy's template pass and racing it. `vscode.json` points at a
marketplace theme and cannot be tinted at all.

### Installing it

Needs `imagemagick`, which Omarchy already has.

```bash
cd ~/.config/omarchy/themes/liquid-glass
mkdir -p ~/.local/bin ~/.config/systemd/user
ln -snf "$PWD/palette/liquid-glass-harmonize" ~/.local/bin/liquid-glass-harmonize
cp palette/liquid-glass-harmonize.{path,service} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now liquid-glass-harmonize.path
```

Symlinked rather than copied so `git pull` updates it. `omarchy theme bg next`
now retunes the palette as it changes the wallpaper.

There is no Omarchy hook for a background change — `omarchy-theme-bg-next` only
swaps a symlink and restarts `swaybg` — so this watches the directory that
symlink lives in. Watching the symlink itself would not work: `ln -nsf`
replaces it, and an inotify watch dies with the thing it was watching.

It writes into `~/.config/omarchy/current/theme/`, never into the repo, and
refuses to run unless that theme is this one — otherwise cycling wallpapers
under another theme would overwrite that theme's terminal configs. A theme
switch wipes the generated files and the watcher regenerates them, so the two
cannot drift.

To turn it off:

```bash
systemctl --user disable --now liquid-glass-harmonize.path
omarchy theme set "Liquid Glass"
```

The second line restores the shipped palette.

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

**The edge does most of the work.** A 3px border with a 90° gradient — white
at the top falling to black at the base, no hue in it — reads as a bevel
catching a single overhead light. At 1px it collapses into a plain outline. In the GTK
surfaces the same idea is an `inset 0 1px 0` highlight plus a vertical
gradient body; remove that one inset shadow and the bar goes flat instantly.

**On windows the rim is real, not painted.** `decoration:glow` is badly named
— it is not an outer bloom but an *inner* one, and it is the only part of this
theme that is computed from a surface's geometry rather than drawn on top of
it. The compositor measures each pixel's distance from the window edge and
fades white inward over 14px, following the same superellipse the corner is
cut on. Where the GTK panels get a one-pixel highlight because that is all
GTK-CSS has, a window gets a genuine ramp. Measured over the shipped
wallpaper, mean luminance of a 400px row at increasing depth below the top
edge:

| depth | 0px | 2px | 4px | 6px | 8px | 10px | 14px |
|---|---|---|---|---|---|---|---|
| off | 28.7 | 29.7 | 30.7 | 31.7 | 32.8 | 33.6 | 35.3 |
| inactive | 50.0 | 44.7 | 41.2 | 37.8 | 36.3 | 35.5 | 35.3 |
| active | 88.3 | 73.3 | 61.0 | 50.7 | 43.8 | 38.9 | 37.1 |

Back on the baseline by about 12px in both states, which is the whole point: a
ramp, not a second border. The falloff is `pow(1 - dist/range, render_power)`,
so `render_power` is the shape knob — at 4 it collapses to a 4px spike that
reads as a doubled outline, and a 20px range at power 3 spreads far enough to
look like haze, which is frost again. 14 and 2 is the pair that ramps.

**The shadow agrees with the rim about where the light is.** It is a gradient
now rather than a flat black — 0.22 at the top falling to 0.52 at the base, on
the same 90° as the border and the inner rim. A cast shadow is not evenly
dark; the light is occluded most directly under the bottom edge. Total weight
is unchanged (the old flat value averaged 0.40, this averages 0.37) — the
shadow did not get heavier, it moved to where `offset = 0 3` was already
pushing it.

**Windows smear when they move.** `decoration:motion_blur`, at 12 samples.
This is the one setting in the theme that is asserted rather than measured,
and the reason is worth stating plainly: motion blur is a function of
per-frame displacement, so every way of photographing it — a screenshot caught
mid-animation, or slowing the animation down until a screenshot can catch it —
destroys the thing being photographed. What is verified is that it loads, that
it engages only during a move or resize, and that it costs nothing at rest.
What it looks like in flight is your call; one line turns it off, in
[Tuning](#tuning).

**Transparency works two different ways, because apps fall into two camps.**

Terminals can render a translucent *background* while keeping glyphs fully
opaque — that's the good kind of glass, and it's why `active_opacity` stays at
`1.0` and each terminal config sets its own alpha (`0.74`) instead.

Everything else — GTK, Electron, browsers — draws an opaque background and
exposes no equivalent knob. Nothing in a theme can change that; Omarchy doesn't
apply a theme `gtk.css`, and Chromium has no transparency setting. The only
lever left is Hyprland window opacity, which fades text along with the
background. So those windows get a mild `opacity 0.92 0.90` — enough that the
blur behind registers as glass, not so much that a page becomes hard to read.
Blur still applies underneath because `blur:ignore_opacity` is on.

The inactive figure is 0.90 rather than 0.86 because that was measured rather
than guessed. Compositing known colour pairs and reading the result back off
the screen, black-on-white keeps 11.7:1 even at 0.86 — body text is never in
danger. What suffers is mid-grey secondary text on a dark UI, the thing every
Electron app labels with: nominally 5.32:1, which clears WCAG AA, and 3.86:1
at 0.86, which does not. 0.90 brings it back to 4.15:1. Full opacity only
measures 5.00:1 here, so no setting fully repairs it — this is the point where
the glass stops paying for itself, not a value to keep pushing.

Media apps are excluded: Omarchy's own rules strip the opacity tags from mpv,
vlc, OBS, Zoom and YouTube tabs, and this theme matches on those tags rather
than on window class, so video stays fully opaque for free.

**The launcher over light windows is the one place this trade-off bites, and
it is only mitigated, not solved.** Every other surface here sits over the
wallpaper, which is nearly black and known in advance. The launcher opens over
whatever you were looking at, and over a white document the page behind used
to lift the panel to near-white and take the near-white text with it. Two
things push back: a dark halo behind the glyphs, which costs nothing against
the wallpaper because it *is* the wallpaper's colour, and a launcher fill at
`0.44` rather than `0.30` — a deliberate exception to clear-not-frosted,
documented at the site in `walker.css`. Measured over a blank white window,
item labels went from 2.3–3.1:1 to 4.1–4.8:1, which clears roughly WCAG AA.

That fill has been wrong in both directions, and the fix was not the one that
looks obvious. At 0.55 it bought contrast and read as a dark slab — the most
opaque surface in a theme whose whole argument is that you can see through it.
At 0.34 it looked right and put body text at 3.2:1. What actually reads as
glass is the rim and the specular, not how thin the body is, so once those
were pushed past their tokens the fill was free to sit where legibility needed
it. The full sweep is in `walker.css`.

The selected row took a second fix of its own. Omarchy's stylesheet paints its
label with the accent, which back when that accent was jade — on a pill this
theme had *also* tinted jade — was low contrast on every backdrop, 2.9:1 even
over the wallpaper, where nothing is washing it out. That label is now the
same near-white as every other row, and the pill's lit gradient and specular
edge carry the "selected" signal instead, which they were already doing
anyway. Over the wallpaper it went 2.9:1 → **5.0:1**, which clears AA
outright; over a white window, 1.7:1 → 2.9:1.

Two things stay short of AA over white, and both are short by construction.
The search placeholder is deliberately half-opacity. The selected row trails
the ordinary rows because the pill it sits on is *lighter* than the panel — a
lit selection and a light backdrop pull in the same direction. Raising the
fill does nothing for either.

**Known limitation:** GTK-CSS cannot sample what is behind a surface, so no
part of this can adapt to the backdrop — there is no `backdrop-luminance` to
respond to and no way to fake one. What is here is a fixed cost paid against
the worst case. A launcher that genuinely adapted would need walker itself to
sample the screen behind it and swap a style class, which is an upstream
feature, not a theme one.

**Corners are squircles.** `rounding = 20` (Hyprland's ceiling) at
`rounding_power = 4.5` gives continuous curvature rather than a circular arc
pasted onto a straight edge — most of what makes a corner look moulded.

**Shell surfaces are layers, not windows**, so they need their own rules —
`layerrule = blur on` per namespace, plus `ignore_alpha` so the clear margin
around a floating panel doesn't get blurred along with the panel.

`xray` is off on purpose: seeing other windows refracted behind the front one
is the layered depth the theme is built around. Turn it on in `hyprland.conf`
to trade that for lower GPU load.

## What a plugin would add, and why there isn't one

Everything above is the compositor's own configuration. That is a deliberate
limit, and it is honest to say what it costs, because the material this theme
is named after does four things nothing here can do.

All four are the same thing underneath: **real glass displaces what is behind
it, and blur only averages it.** Refraction is a UV offset driven by a height
field — steep at the rim, flat in the middle — so content near the edge is
pulled in from beyond the surface's own bounds. Chromatic dispersion falls out
of sampling red, green and blue at slightly different refraction scales, which
is what puts a spectral fringe on an edge. Fresnel makes the rim more
reflective at a glancing angle. And an adaptive material samples its own
backdrop and changes tint so that foreground text stays legible over anything.

Hyprland's blur is a Kawase blur. It can average neighbouring pixels and it
cannot move them, so none of the four is reachable from a config file at any
setting. What this theme does instead is paint a very careful still life of
the result: a lit rim, a bevel, a graded body, a shadow that agrees about the
light. The parts that are computed rather than painted — the compositor's
inner rim, the superellipse corners — are the parts that hold up best when you
look closely, which is the tell.

Plugins exist that do the real thing. [hyprglass](https://github.com/hyprnux/hyprglass)
and [liquid-glass-plugin-hyprpm](https://github.com/purple-lines/liquid-glass-plugin-hyprpm)
both implement edge refraction, chromatic aberration, fresnel and specular
highlights, and hyprglass reaches layer surfaces too, which matters because
most of this theme *is* layer surfaces. Its `adaptive_dim` and `adaptive_boost`
are the backdrop-sampling that `walker.css` correctly calls impossible in
GTK-CSS — impossible there, entirely possible in the compositor.

They are not used here, and the reason is the first line of this section. A
plugin is compiled against one exact Hyprland ABI and breaks on the next
release; hyprglass hooks private internals to reach layer surfaces at all.
A theme that needed one would be a theme that stops working on a Tuesday
because Hyprland shipped a point release, and "clone it and it works" is worth
more than a fringe on an edge. If you want the fringe, install one of them
yourself — nothing in this theme conflicts with either.

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
| `gtk.css` | translucent GTK4 window backgrounds — **install by hand**, see below |
| `palette/` | optional: retune the ANSI palette to the wallpaper's hue on every change |
| `icons/` | hueless glass folder icons — **install by hand**, see `icons/README.md` |
| `backgrounds/` | six wallpapers |

Each of those files carries a comment explaining *why* it looks the way it
does — for most of them, why they override Omarchy's generated template —
worth reading before changing one.

## Tuning

Everything in this section goes in `~/.config/hypr/looknfeel.conf`, which
Omarchy sources *after* the theme — so anything you put there wins, and an
update or a theme switch will not overwrite it.

### Profile: lite

For integrated graphics, or anything where the fans come on when you open the
launcher. Blur cost scales with passes, and `xray` is the big one: it blurs
only the wallpaper rather than resampling the windows stacked behind each
surface.

```ini
decoration:blur:passes = 2      # from 3
decoration:blur:xray   = true   # blur only the wallpaper, not windows behind
```

You lose the layered depth — windows behind the front one stop showing through
as refraction — which is the thing the theme is built around, so try `passes`
alone first and add `xray` only if that is not enough.

### Profile: reduced motion

Neither Hyprland nor GTK has a `prefers-reduced-motion` equivalent, so there
is nothing to switch on — the durations have to be overridden directly.

```ini
animations {
    # A straight line: no ease, no overshoot, no settle.
    bezier = instant, 0, 0, 1, 1

    # Speeds are in deciseconds, so 0.5 is 50ms — short enough not to read as
    # motion, long enough that surfaces do not visibly pop in and out.
    animation = layersIn,   1, 0.5, instant, fade
    animation = layersOut,  1, 0.5, instant, fade
    animation = windows,    1, 0.5, instant
    animation = windowsIn,  1, 0.5, instant
    animation = windowsOut, 1, 0.5, instant
    animation = fade,       1, 0.5, instant
    animation = workspaces, 0, 0,   instant
}
```

For no motion at all, `animations { enabled = false }` on its own is enough
and overrides everything above.

That covers the compositor. The bar and the launcher animate in GTK-CSS, which
`looknfeel.conf` cannot reach — those two transitions live in `waybar.css` and
`walker.css`, both marked with a comment about the overshoot. Delete the
`transition:` line in each, or drop the cubic-bezier for a plain `linear`, and
run `omarchy restart waybar`.

### Making the launcher settle like everything else

The `layersIn`/`layersOut` curves in `hyprland.conf` reach the OSD,
notifications, the logout dialog and the bar — but not walker. Omarchy ships
`layerrule = no_anim on, match:namespace walker`, and it is sourced before the
theme, so the launcher opens instantly while every other surface eases in.

That is upstream's call about how fast a launcher should feel, so the theme
leaves it alone. To take it back:

```ini
layerrule = no_anim off, match:namespace walker
```

Later rules win, so this belongs in `looknfeel.conf` like everything else in
this section. Blur and the `ignore_alpha` threshold already apply to walker
either way — `no_anim` only governs animation.

### The inner rim, and turning the motion off

Two settings people are most likely to want to move. Both are compositor
options, so `looknfeel.conf` reaches them:

```ini
# The rim: brighter, or wider, or gone.
decoration:glow:enabled      = false   # off entirely
decoration:glow:range        = 20      # from 14 — wider ramp, closer to haze
decoration:glow:render_power = 4       # from 2  — tighter, reads as a second outline

# The smear on moving and resizing windows.
decoration:motion_blur:enabled = false
decoration:motion_blur:samples = 7     # from 12 — Hyprland's default, cheaper
```

There is no per-window escape hatch for the rim. `no_blur`, `no_shadow` and
`no_dim` all exist as window rules; `no_glow` does not. So a *windowed* video
player gets a faint white edge inside its frame and no rule can exempt it.

Fullscreen is exempt, which covers the case where it would actually bother
you, and that was checked rather than assumed — with the glow forced to opaque
red at range 40, a fullscreen window reads 12.5 mean red at its top edge and
11.8 thirteen pixels in — flat, and that is the terminal's own content with no
red in it anywhere. A windowed one reads 213.8 falling to 94.9 over the same
distance.

### Blur on the lock screen

0.56 added `misc:session_lock_blur`, and the theme leaves it off deliberately.
Its own help text says you probably want `misc:session_lock_xray` with it, and
that option keeps your workspaces rendering underneath the lock surface.
Against Omarchy's hyprlock, which draws an opaque wallpaper, that renders a
desktop nobody can see and bills the GPU for it. Against a hyprlock someone
has made translucent, it puts the contents of their session on the lock
screen — blurred, but there.

A lock screen exists to not show you the desktop, so that is not a switch a
theme should throw on a user's behalf. If you want it, you want it knowingly:

```ini
misc:session_lock_blur = true
misc:session_lock_xray = true
```

### Frost instead of clear

Want it frosted instead of clear? Push the two settings that define the
difference:

```ini
decoration:blur:size  = 8       # from 4
decoration:blur:noise = 0.02    # from 0.003 — grain is what reads as "frosted"
```

Clearer or more solid *terminals*: `opacity` in `alacritty.toml`,
`background-opacity` in `ghostty.conf`, `background_opacity` in `kitty.conf`,
`alpha` in `foot.ini`. Below about `0.65` text starts to fight the wallpaper.

Clearer or more solid *everything else* — the three `windowrule = opacity`
lines at the bottom of `hyprland.conf`. Toward `1.0` if text looks too soft,
toward `0.85` for more glass. The second number is the unfocused one and is
where the contrast goes first; see the measurements in the comment above
those lines before lowering it.

## Wallpapers

Six, the same wordmark in six hues: jade, sapphire, amber, crimson, magenta,
violet. `1-omarchy-liquid-glass.png` is the default.

They matter more here than in a normal theme. The surfaces carry no colour of
their own, so whichever of these is up decides what the entire desktop looks
like — bar, launcher, notifications and folder icons all take their hue from
it. Switching wallpaper switches the theme, and nothing needs retuning.

`omarchy theme bg next` cycles them.

Your own work too: anything dark with large smooth forms suits this, because a
panel laid over something that curves reads as glass resting on glass, while a
panel over a flat wash reads as a sticker. Drop files into this directory and
they join the cycle.

The five colour variants are 1672x941 rather than 1920x1080 — that is the size
they were made at, and `swaybg -m fill` scales them, so they are very slightly
softer than the jade original on a 1080p panel.

## Notes

- Icons are the theme's own hueless glass folders (`icons/`), inheriting
  everything else from `Yaru-prussiangreen-dark`. That inherited set does carry
  a hue, but the icons Yaru actually tints are the folders, and those are the
  ones overridden here — including `user-desktop`, `folder-new` and
  `folder-drag-accept`, which are easy to miss because nothing names them
  "folder". What is left green is a handful of accented arrows and the
  third-party folders (`folder-dropbox`, `insync-folder`), which are better
  off staying identifiable.
- VS Code points at **Ocean Green: Dark** (`jovejonovski.ocean-green`), the
  closest dark theme on the marketplace; Omarchy installs it on first switch.
- Neovim needs `bjarneo/aether.nvim`, which LazyVim will fetch on next start.

## Licence

MIT. The wallpapers are included under the same terms.

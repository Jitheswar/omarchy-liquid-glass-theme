#!/usr/bin/env python3
"""Pull the ANSI palette toward the hue of the current wallpaper.

The surfaces in this theme have no colour of their own, so they take the
wallpaper's. The terminal palette could not: those sixteen hues are fixed, and
on a magenta wallpaper green directory names sit on a magenta field with
nothing making them agree. This closes that gap.

It is a *rotation*, not an extraction. Palette-from-image tools (pywal and
friends) replace the sixteen colours with whatever the picture happens to
contain, which loses the two properties the palette exists for: red has to stay
the colour `git diff` deletes in and green the colour it adds in, and the
sixteen have to stay far enough apart that syntax does not collapse into mush.

So each colour keeps its own hue and is pulled a bounded fraction of the way
toward the wallpaper's, in OKLCh, with lightness and chroma held exactly. Two
things follow by construction rather than by measurement:

  - contrast against the terminal background cannot change, because contrast is
    a function of lightness and lightness is what we hold;
  - no colour crosses into another's name, because MAX_SHIFT is set from a
    measured sweep of the tightest pair in the palette across every shipped
    wallpaper. See the constant.

The effect is meant to be felt rather than noticed. It is a cast, not a
recolour: on the magenta wallpaper the greens warm slightly and the blues cool
slightly, and `ls` still paints a directory in something you would call green.

One neutral is touched, and it is the one you spend all day reading. The
terminal's foreground takes the wallpaper's hue at a fixed low chroma, holding
its lightness exactly — see TEXT_CHROMA. Everything else stays hueless:
background, cursor, accent, the selection pair and the ANSI greys are the
glass, and glass has no colour.

Usage:
    harmonize.py <wallpaper.png> --out <dir>     write the palette files
    harmonize.py <wallpaper.png> --print         show the derived palette
"""

import math
import os
import re
import subprocess
import sys

# <repo>/palette/harmonize.py -> <repo>. Used to read the shipped neovim.lua.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The single knob. How far, in OKLCh degrees, a colour may be pulled toward the
# wallpaper's hue.
#
# This is bounded low, and the bound was measured rather than picked. Pulling
# every colour toward one point compresses the wheel — colours on opposite
# sides of the target close on each other — and the palette's tightest pair is
# blue (229) and cyan (203), only 26 degrees apart to start with. Sweeping the
# six shipped wallpapers, worst-case separation across all of them:
#
#     max shift    tightest pair    what breaks
#        30            14.3         red lands on orange, cyan lands on blue
#        20            17.1         yellow starts reading as olive
#        15            20.7         -
#        12            22.3         -   <- here
#         6            26.0         barely visible
#
# 12 is the most movement that costs nothing nameable: every colour stays
# inside its own name on every wallpaper, and the tightest pair keeps 22 of its
# original 26 degrees. Raise it if you want the effect stronger, but read the
# table first — past 15 this stops being harmonisation and starts being a
# different palette, and `git diff` deletions stop being red.
MAX_SHIFT = 12.0

# Fraction of the distance to the target hue, before MAX_SHIFT clamps it. Below
# 1.0 so a colour already near the wallpaper's hue moves proportionally less
# than one far from it, which spreads the compression evenly instead of
# bunching it on one side of the wheel.
PULL = 0.30

# Pixels below this OKLCh chroma are grey and carry no hue worth aiming at.
# The wallpapers here are mostly near-black, so without this the dominant hue
# is whatever noise sits in the shadows.
MIN_CHROMA = 0.04


# ── OKLab / OKLCh ─────────────────────────────────────────────────────────
# Björn Ottosson's OKLab. Used rather than HSL because HSL's "hue" is not
# perceptual: rotating blue by 30 degrees there changes its lightness visibly,
# which would break the contrast guarantee above.

def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _cbrt(x):
    return math.copysign(abs(x) ** (1 / 3), x)


def rgb_to_oklab(rgb):
    r, g, b = (_srgb_to_linear(v / 255) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = _cbrt(l), _cbrt(m), _cbrt(s)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab):
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )
    return tuple(_linear_to_srgb(v) for v in lin)


def to_lch(rgb):
    L, a, b = rgb_to_oklab(rgb)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def from_lch(L, C, h):
    """Back to 8-bit sRGB, reducing chroma until the colour is in gamut.

    A rotation can push a colour outside sRGB even though its source was
    inside — the gamut is not a cylinder. Clipping the channels would change
    lightness, so chroma is bisected down instead, which keeps L exact and
    gives up only the saturation that could not be shown anyway.
    """
    rad = math.radians(h)

    def attempt(c):
        return oklab_to_rgb((L, c * math.cos(rad), c * math.sin(rad)))

    def in_gamut(v):
        return all(-1e-6 <= x <= 1 + 1e-6 for x in v)

    if not in_gamut(attempt(C)):
        lo, hi = 0.0, C
        for _ in range(24):
            mid = (lo + hi) / 2
            if in_gamut(attempt(mid)):
                lo = mid
            else:
                hi = mid
        C = lo
    return tuple(min(255, max(0, round(v * 255))) for v in attempt(C))


def hex_of(rgb):
    return "#%02X%02X%02X" % rgb


def parse_hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


# ── The wallpaper's hue ───────────────────────────────────────────────────

def dominant_hue(path, samples=160):
    """Circular mean of the wallpaper's hues, weighted by chroma and lightness.

    A circular mean rather than a histogram peak: these wallpapers are a single
    wash rather than a photograph, so there is one hue and averaging finds it
    without the bin-boundary sensitivity a peak would have. Weighted by chroma
    so the near-black field does not drag the answer, and by lightness so the
    hue you actually see wins over the same hue at 2% brightness.
    """
    out = subprocess.run(
        ["magick", path, "-resize", f"{samples}x", "-depth", "8", "txt:-"],
        capture_output=True, text=True, check=True,
    ).stdout
    x = y = 0.0
    for r, g, b in re.findall(r": \((\d+),(\d+),(\d+)\)", out):
        L, C, h = to_lch((int(r), int(g), int(b)))
        if C < MIN_CHROMA:
            continue
        w = C * L
        rad = math.radians(h)
        x += w * math.cos(rad)
        y += w * math.sin(rad)
    if x == 0 and y == 0:
        return None  # a genuinely grey wallpaper; nothing to aim at
    return math.degrees(math.atan2(y, x)) % 360


def shift_toward(h, target):
    delta = (target - h + 180) % 360 - 180
    return (h + max(-MAX_SHIFT, min(MAX_SHIFT, PULL * delta))) % 360


def harmonize(colour, target):
    L, C, h = to_lch(colour)
    if C < MIN_CHROMA:
        return colour  # a neutral stays neutral
    return from_lch(L, C, shift_toward(h, target))


# ── The palette ───────────────────────────────────────────────────────────
# The base values, copied from colors.toml. Only the sixteen ANSI slots are
# listed: everything structural in that file is a grey and would be returned
# unchanged anyway, so leaving it out states the intent instead of relying on
# the chroma test to notice.

BASE = {
    "color0": "#1A1A1A", "color1": "#F2798F", "color2": "#6FBF7A", "color3": "#E5CE8A",
    "color4": "#6FB6D6", "color5": "#B49BE0", "color6": "#74C7CE", "color7": "#C6C6C6",
    "color8": "#6E6E6E", "color9": "#FF97A8", "color10": "#8FD895", "color11": "#F5E2A8",
    "color12": "#96CFE8", "color13": "#CBB6F0", "color14": "#96DCE2", "color15": "#F2F2F2",
}

# Hues that live outside the ANSI sixteen but still need to move with them.
# aether has an orange slot the terminals have no equivalent for; leaving it
# behind would make the editor disagree with the terminal it runs inside.
EXTRA = {"orange": "#EFAE8C"}

# Untouched, and listed so the writers below have one place to read them from.
NEUTRALS = {
    "foreground": "#E0E0E0", "background": "#0A0A0A", "cursor": "#FFFFFF",
    "selection_foreground": "#0A0A0A", "selection_background": "#C8C8C8",
    "accent": "#FFFFFF",
}

ALPHA = "0.74"

# Chroma for the browser's seed colour, in OKLCh.
#
# Chromium and Brave do not use this as a fill — they expand it into a whole
# Material You chrome, which amplifies it hard. The old jade seed #070E0C had
# chroma 0.0122 and produced a browser that read as unmistakably green, so this
# is the level at which the tint is clearly visible rather than a level chosen
# to be subtle. Matching that number means the *strength* of the tint is the one
# the theme already shipped and only its hue is new.
#
# This is the one surface that has to bake the wallpaper's colour in rather than
# take it through glass. Terminals stay neutral because at alpha 0.74 the
# wallpaper is genuinely behind them; a browser draws opaque and Chromium
# exposes no transparency, so a neutral seed there is simply grey.
CHROME_CHROMA = 0.0122

# Chroma for the terminal's foreground text, in OKLCh.
#
# The sixteen ANSI slots can only be pulled MAX_SHIFT degrees before `git diff`
# deletions stop being red, so hue rotation alone can never make a terminal
# read as part of the desktop — and it was aimed at the wrong text anyway. The
# hues are what `ls` and a syntax highlighter use. Everything else on the
# screen, which is most of what is on the screen, is drawn in `foreground`, and
# that was a flat neutral grey sitting on a wallpaper-lit pane.
#
# So this tints the one colour that carries the bulk of the text, and it is the
# cheapest tint in the file: a neutral has no name to cross into. Green can
# stop looking green and that costs a reading; off-white cannot stop looking
# off-white. Lightness is held exactly, so contrast against the background is
# unchanged by construction — measured at 14.998 before and 14.93 after, on a
# scale where the drift is quantisation.
#
# Higher than CHROME_CHROMA above, and deliberately. That number is a *seed*:
# Chromium expands it into a whole Material You chrome and amplifies it hard,
# so a small value arrives loud. Text is not amplified — what is set here is
# what lands on the glass — so matching the browser's number would have made
# the terminal the quieter of the two.
TEXT_CHROMA = 0.018


def derive(wallpaper):
    target = dominant_hue(wallpaper)
    source = dict(BASE, **EXTRA)
    if target is None:
        return source, None
    out = {k: hex_of(harmonize(parse_hex(v), target)) for k, v in source.items()}
    return out, target


def chrome_seed(target):
    """The browser's opaque stand-in for glass.

    Held at the neutral background's lightness so the browser stays as dark as
    every other surface, and given the wallpaper's hue at a fixed low chroma.
    A grey wallpaper leaves it exactly neutral.
    """
    L, _, _ = to_lch(parse_hex(NEUTRALS["background"]))
    if target is None:
        return parse_hex(NEUTRALS["background"])
    return from_lch(L, CHROME_CHROMA, target)


def text_neutrals(target):
    """NEUTRALS with the terminal's foreground carrying the wallpaper's hue.

    Only `foreground` moves, and only in chroma — its lightness is the value
    every contrast figure in the theme was measured against, so it is held
    exactly. A grey wallpaper leaves the whole dict untouched.
    """
    if target is None:
        return dict(NEUTRALS)
    L, _, _ = to_lch(parse_hex(NEUTRALS["foreground"]))
    return dict(NEUTRALS, foreground=hex_of(from_lch(L, TEXT_CHROMA, target)))


# ── Writers ───────────────────────────────────────────────────────────────
# One per terminal, each producing the same file the theme ships by hand, so a
# harmonised install and a plain one differ only in the sixteen values.

HEADER = "# Generated by palette/harmonize.py from {wallpaper}\n# Edits here are overwritten on the next wallpaper change.\n"

ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def write_alacritty(p, n, wallpaper, target=None, source_dir=None):
    rows = "\n".join(f'{name} = "{p["color%d" % i]}"' for i, name in enumerate(ANSI_NAMES))
    bright = "\n".join(f'{name} = "{p["color%d" % (i + 8)]}"' for i, name in enumerate(ANSI_NAMES))
    return f"""{HEADER.format(wallpaper=wallpaper)}
[window]
opacity = {ALPHA}

[colors.primary]
background = "{n['background']}"
foreground = "{n['foreground']}"

[colors.cursor]
text = "{n['background']}"
cursor = "{n['cursor']}"

[colors.vi_mode_cursor]
text = "{n['background']}"
cursor = "{n['cursor']}"

[colors.search.matches]
foreground = "{n['background']}"
background = "{p['color3']}"

[colors.search.focused_match]
foreground = "{n['background']}"
background = "{p['color1']}"

[colors.footer_bar]
foreground = "{n['background']}"
background = "{n['foreground']}"

[colors.selection]
text = "{n['selection_foreground']}"
background = "{n['selection_background']}"

[colors.normal]
{rows}

[colors.bright]
{bright}
"""


def write_kitty(p, n, wallpaper, target=None, source_dir=None):
    body = "\n".join(f"color{i} {p['color%d' % i]}" for i in range(16))
    return f"""{HEADER.format(wallpaper=wallpaper)}
background_opacity {ALPHA}

foreground {n['foreground']}
background {n['background']}
selection_foreground {n['selection_foreground']}
selection_background {n['selection_background']}

cursor {n['cursor']}
cursor_text_color {n['background']}

active_border_color {n['accent']}
active_tab_background {n['accent']}

{body}
"""


def write_ghostty(p, n, wallpaper, target=None, source_dir=None):
    body = "\n".join(f"palette = {i}={p['color%d' % i]}" for i in range(16))
    return f"""{HEADER.format(wallpaper=wallpaper)}
background-opacity = {ALPHA}

background = {n['background']}
foreground = {n['foreground']}
cursor-color = {n['cursor']}
selection-background = {n['selection_background']}
selection-foreground = {n['selection_foreground']}

{body}
"""


def write_foot(p, n, wallpaper, target=None, source_dir=None):
    def block():
        rows = [
            f"foreground={n['foreground'].lstrip('#')}",
            f"background={n['background'].lstrip('#')}",
            f"selection-foreground={n['selection_foreground'].lstrip('#')}",
            f"selection-background={n['selection_background'].lstrip('#')}",
            "",
            f"cursor={n['background'].lstrip('#')} {n['cursor'].lstrip('#')}",
            "",
        ]
        rows += [f"regular{i}={p['color%d' % i].lstrip('#')}" for i in range(8)]
        rows.append("")
        rows += [f"bright{i}={p['color%d' % (i + 8)].lstrip('#')}" for i in range(8)]
        return "\n".join(rows)

    return f"""{HEADER.format(wallpaper=wallpaper)}
[colors]
alpha={ALPHA}

{block()}

[colors-dark]
{block()}
"""


def write_chromium(p, n, wallpaper, target=None):
    """Decimal "R,G,B" — the format omarchy-theme-set-browser parses.

    No comment header is possible: the file is read with `$(<file)` and fed
    straight to printf, so anything but the one line would break it.
    """
    return "%d,%d,%d\n" % chrome_seed(target)


def write_neovim(p, n, wallpaper, target=None, source_dir=None):
    """The shipped neovim.lua with its palette hexes swapped, nothing else.

    A substitution rather than a template on purpose. aether takes an explicit
    colour table *and* an on_highlights function, and templating the whole file
    would mean this generator silently owning a hand-maintained one — every
    future edit to the real neovim.lua would have to be mirrored here or be
    quietly dropped whenever harmonizing is switched on. Rewriting only the hex
    literals we know the meaning of keeps that file the single source of its own
    structure.
    """
    path = os.path.join(source_dir or REPO, "neovim.lua")
    with open(path) as f:
        text = f.read()
    for key, original in dict(BASE, **EXTRA).items():
        if p[key].upper() != original.upper():
            text = re.sub(re.escape(original), p[key], text, flags=re.IGNORECASE)
    return text


WRITERS = {
    "alacritty.toml": write_alacritty,
    "kitty.conf": write_kitty,
    "ghostty.conf": write_ghostty,
    "foot.ini": write_foot,
    "chromium.theme": write_chromium,
    "neovim.lua": write_neovim,
}


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().split("Usage:")[-1].strip(), file=sys.stderr)
        return 2
    wallpaper = argv[1]
    palette, target = derive(wallpaper)

    if "--print" in argv:
        print(f"wallpaper hue: {'none (grey)' if target is None else f'{target:.1f} deg'}")
        for k, v in BASE.items():
            moved = palette[k]
            L, C, h = to_lch(parse_hex(v))
            if C < MIN_CHROMA:
                print(f"  {k:8} {v}            neutral, untouched")
            else:
                _, _, h2 = to_lch(parse_hex(moved))
                print(f"  {k:8} {v} -> {moved}   hue {h:5.1f} -> {h2:5.1f}")
        fg = text_neutrals(target)["foreground"]
        if fg == NEUTRALS["foreground"]:
            print(f"  {'text':8} {NEUTRALS['foreground']}            neutral, untouched")
        else:
            print(f"  {'text':8} {NEUTRALS['foreground']} -> {fg}   chroma 0 -> {TEXT_CHROMA}")
        return 0

    if "--out" not in argv:
        print("need --out <dir> or --print", file=sys.stderr)
        return 2
    out = argv[argv.index("--out") + 1]
    for name, writer in WRITERS.items():
        with open(os.path.join(out, name), "w") as f:
            f.write(writer(palette, text_neutrals(target), os.path.basename(wallpaper), target))
    print(f"harmonized {len(WRITERS)} files to hue "
          f"{'none (grey wallpaper)' if target is None else f'{target:.0f}'} in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

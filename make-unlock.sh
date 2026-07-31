#!/bin/bash
#
# Liquid Glass — regenerate unlock.png.
#
# unlock.png is the logo Plymouth shows while the disk is being unlocked and
# the system is booting. `omarchy plymouth set-by-theme liquid-glass` reads it
# straight out of this directory, together with `background` and `foreground`
# from colors.toml, and refuses to run without it — so before this file existed
# the command exited with "Logo file not found" and Liquid Glass was the one
# theme that could not reach the boot screen. Every theme Omarchy ships has one.
#
# It is generated rather than drawn, and committed rather than generated at
# install time, because Plymouth runs from the initramfs where none of this is
# available. Re-run it only if the source mark or the palette changes.
#
# The design follows the same rule the rest of the theme does: this theme has
# no accent hue, so where other themes tint the mark — jade, pink, lavender —
# this one leaves it white and spends the difference on light instead. The
# vertical ramp is the same overhead source as the window border, the inner rim
# and the shadow in hyprland.conf: bright along the top edge, falling toward
# the base. The bloom underneath is what a lit sign does to the dark around it,
# and it is the only part of this theme that is allowed to glow outward rather
# than inward — a boot screen is one flat surface with nothing behind it to
# refract, so there is no glass to be had, only light.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

SRC="${OMARCHY_PATH:-$HOME/.local/share/omarchy}/logo.svg"
OUT=unlock.png

# 1108x523 is the size every stock theme's unlock.png uses. Plymouth scales the
# logo to the screen, so the number that matters is the ratio, not the pixels —
# matching it keeps this theme the same size as the others on the same monitor.
CANVAS_W=1108
CANVAS_H=523
MARK_W=980   # leaves room either side for the bloom to fall off inside the canvas

[[ -f $SRC ]] || { echo "error: $SRC not found (is Omarchy installed?)" >&2; exit 1; }
command -v magick >/dev/null || { echo "error: imagemagick not installed" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# The source mark is filled #000 on transparency, so its alpha channel *is* the
# shape. Everything below paints through that alpha rather than recolouring
# pixels, which is what keeps the edges clean at this scale.
magick -background none "$SRC" -resize ${MARK_W}x "$tmp/mask.png"
W=$(magick identify -format '%w' "$tmp/mask.png")
H=$(magick identify -format '%h' "$tmp/mask.png")

# The bevel. glass-specular (0.34 over white, so effectively full white) at the
# top edge, down to the theme's own foreground at the base — the same direction
# and the same restraint as `$activeBorderColor`, which runs FFFFFFF2 at the
# top and lands near black at the bottom. A flat #EDEDED fill was tried first
# and reads as a sticker; the ramp is what makes it look lit.
magick -size "${W}x${H}" gradient:'#FFFFFF-#B8B8B8' "$tmp/ramp.png"
magick "$tmp/ramp.png" "$tmp/mask.png" -compose CopyOpacity -composite "$tmp/mark.png"

# The bloom. Built from a flat white copy of the shape rather than from the
# bevelled mark, because a blurred *gradient* is smeared paint and what is
# wanted is light: the falloff should carry the mark's outline, not its shading.
magick -size "${W}x${H}" xc:white "$tmp/mask.png" -compose CopyOpacity -composite "$tmp/lit.png"

# Two passes at different radii rather than one. A single wide blur gives an
# even haze, and light around a bright object does not fall off evenly — it is
# concentrated close in and trails off far out. The tight pass carries the
# halo, the wide one the ambience.
magick "$tmp/lit.png" -channel A -blur 0x10 -evaluate multiply 0.50 +channel "$tmp/glow-near.png"
magick "$tmp/lit.png" -channel A -blur 0x30 -evaluate multiply 0.18 +channel "$tmp/glow-far.png"

magick -size "${CANVAS_W}x${CANVAS_H}" xc:none \
  "$tmp/glow-far.png"  -gravity center -compose over -composite \
  "$tmp/glow-near.png" -gravity center -compose over -composite \
  "$tmp/mark.png"      -gravity center -compose over -composite \
  -define png:color-type=6 "$OUT"

magick identify "$OUT"
echo "wrote $OUT"

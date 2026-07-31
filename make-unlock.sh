#!/bin/bash
#
# Liquid Glass — regenerate unlock.png and preview-unlock.png.
#
# Two files, and they are for two different audiences.
#
# **unlock.png** is the logo Plymouth shows while the disk is being unlocked
# and the system is booting. `omarchy plymouth set-by-theme liquid-glass` reads
# it straight out of this directory, together with `background` and
# `foreground` from colors.toml, and refuses to run without it — so before this
# file existed the command exited with "Logo file not found" and Liquid Glass
# was the one theme that could not reach the boot screen at all.
#
# **preview-unlock.png** is what puts the theme in the catalogue under
# **Omarchy menu → Style → Unlock**, and its presence is the whole gate.
# `default/elephant/omarchy_unlocks.lua` walks ~/.config/omarchy/themes and
# $OMARCHY_PATH/themes, and lists a theme only `if file_exists(preview_path)` —
# so a theme with a perfectly good unlock.png and no preview simply is not
# offered, which is where this one was. Choosing an entry runs
# `omarchy-plymouth-set-by-theme` in a floating terminal so sudo can prompt;
# nothing is applied until someone picks it, which is the point of listing it
# there rather than doing anything at install time.
#
# The preview is generated from omarchy.script's own geometry rather than
# drawn, so it cannot drift from what actually boots — and it includes the
# padlock and password field for the same reason: those are Plymouth's, they
# are what the user will really see, and a preview showing only the logo would
# be a picture of something that never appears on screen.
#
# Both are committed rather than generated at install time, because Plymouth
# runs from the initramfs where none of this is available. Re-run it only if
# the source mark or the palette changes.
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

# ── Why the canvas hugs the mark ──────────────────────────────────────────
# The first version of this used 1108x523, on the reasoning that it is what
# every stock theme's unlock.png measures. That was the wrong thing to copy,
# and simulating the boot screen is what showed it.
#
# Plymouth does not draw this logo on its own. It draws a password field too —
# omarchy.script positions `entry.png` at `logo.y + logo.height + 40`, with a
# padlock to its left and bullets inside it as you type — and the offset is
# measured from the logo *image*, not from the ink in it. The stock logos fill
# their canvas edge to edge, so 40px of image is 40px of visible gap. This one
# is a mark on a transparent field with room left for the bloom, so every pixel
# of padding pushed the password box further away: at 523 tall against a 230px
# mark, the field landed ~186px below the wordmark and the two read as
# unrelated things on the screen rather than one prompt.
#
# So the canvas is derived from the mark instead of fixed, and the margin is
# the smallest one the bloom can live inside. The 40px Plymouth adds is then
# roughly the 40px it was designed to be.
#
# MARK_W is 860 rather than 980 for the same reason: on a 1920px screen the
# stock marks occupy ~42% of the width, and Plymouth renders the logo at native
# size without scaling, so this is the one place where the pixel count decides
# how big the thing actually looks at boot. Matching that keeps Liquid Glass
# from being the one theme whose boot screen is noticeably larger than the rest.
MARK_W=860
MARGIN=46

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
CANVAS_W=$(( W + MARGIN * 2 ))
CANVAS_H=$(( H + MARGIN * 2 ))

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
#
# Both radii are sized to die out inside MARGIN. A Gaussian is spent by ~3σ, so
# the wide pass at σ=15 is gone by 45px and the margin is 46 — the bloom
# reaches the edge of the canvas and nothing is clipped. Widening one without
# the other leaves a hard rectangular cut where the glow meets the boundary.
magick "$tmp/lit.png" -channel A -blur 0x8  -evaluate multiply 0.50 +channel "$tmp/glow-near.png"
magick "$tmp/lit.png" -channel A -blur 0x15 -evaluate multiply 0.20 +channel "$tmp/glow-far.png"

magick -size "${CANVAS_W}x${CANVAS_H}" xc:none \
  "$tmp/glow-far.png"  -gravity center -compose over -composite \
  "$tmp/glow-near.png" -gravity center -compose over -composite \
  "$tmp/mark.png"      -gravity center -compose over -composite \
  -define png:color-type=6 "$OUT"

magick identify "$OUT"
echo "wrote $OUT"

# ── preview-unlock.png ────────────────────────────────────────────────────
# The catalogue entry, composed exactly the way Plymouth will compose it:
#
#   logo.y  = H/2 - logo.h/2
#   entry.y = logo.y + logo.h + 40      entry.x = W/2 - entry.w/2
#   lock    = scaled to 0.8 * entry.h, 15px to the left of entry
#   bullets = 7x7, from entry.x + 20, every 12px
#
# Those five lines are omarchy.script's, transcribed rather than invented, and
# transcribing them is what caught the bug this file's geometry section is
# about. Judging a boot logo on its own is judging half the screen.
#
# The colours come out of colors.toml rather than being written here, because
# omarchy-plymouth-set-by-theme reads them from there too — a preview that
# hardcoded them would keep looking right after the palette stopped matching.

PREVIEW=preview-unlock.png
SCREEN_W=1920
SCREEN_H=1080
PLY="${OMARCHY_PATH:-$HOME/.local/share/omarchy}/default/plymouth"

BG=$(awk -F'"' '/^background/{print $2}' colors.toml)
FG=$(awk -F'"' '/^foreground/{print $2}' colors.toml)

if [[ ! -d $PLY ]]; then
  echo "note: $PLY not found; skipping $PREVIEW" >&2
  exit 0
fi

# omarchy-plymouth-set recolours these four with the theme's text colour on the
# way in, so the preview has to do the same or it shows the wrong hardware.
for a in entry lock bullet; do
  magick "$PLY/$a.png" -channel RGB +level-colors "$FG","$FG" "$tmp/$a.png"
done

lw=$(magick identify -format '%w' "$OUT"); lh=$(magick identify -format '%h' "$OUT")
ew=$(magick identify -format '%w' "$tmp/entry.png"); eh=$(magick identify -format '%h' "$tmp/entry.png")

ly=$(( SCREEN_H / 2 - lh / 2 )); lx=$(( SCREEN_W / 2 - lw / 2 ))
ey=$(( ly + lh + 40 ));          ex=$(( SCREEN_W / 2 - ew / 2 ))

# The lock is 84x96 at source; the script scales it by height and lets the
# width follow, so the same arithmetic is repeated here rather than guessed.
lock_h=$(( eh * 8 / 10 ))
lock_w=$(( 84 * lock_h / 96 ))
magick "$tmp/lock.png" -resize "${lock_w}x${lock_h}!" "$tmp/lock-scaled.png"
lock_x=$(( ex - lock_w - 15 ))
lock_y=$(( ey + eh / 2 - lock_h / 2 ))

magick "$tmp/bullet.png" -resize 7x7! "$tmp/bullet-scaled.png"

# Four bullets, as if a password were part-typed. An empty field photographs as
# an empty box and reads as decoration; four dots say "this is where you type".
compose=(-size "${SCREEN_W}x${SCREEN_H}" "xc:$BG"
  "$OUT"                   -geometry "+${lx}+${ly}"           -compose over -composite
  "$tmp/entry.png"         -geometry "+${ex}+${ey}"           -compose over -composite
  "$tmp/lock-scaled.png"   -geometry "+${lock_x}+${lock_y}"   -compose over -composite)
for i in 0 1 2 3; do
  compose+=("$tmp/bullet-scaled.png"
            -geometry "+$(( ex + 20 + i * 12 ))+$(( ey + eh / 2 - 3 ))"
            -compose over -composite)
done

# Forced to sRGB. Every colour on this screen is neutral grey — the background,
# the mark, the field — so ImageMagick will happily detect that and write a
# Grayscale PNG. It renders identically, but every stock preview-unlock.png is
# sRGB, and being the one file in the set with a different colour type is a
# thing to be deliberate about rather than to discover later.
magick "${compose[@]}" -colorspace sRGB -type TrueColor "$PREVIEW"

magick identify "$PREVIEW"
echo "wrote $PREVIEW — this is what lists the theme under Style → Unlock"

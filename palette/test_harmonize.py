#!/usr/bin/env python3
"""Check that harmonizing a palette cannot break it.

The whole argument for rotating hue in OKLCh rather than extracting a palette
from the image is that two properties survive the rotation. This asserts both,
against every wallpaper the theme ships, so a change to MAX_SHIFT or PULL that
looks fine on one wallpaper cannot quietly ruin another.

Run:  python3 palette/test_harmonize.py
"""

import importlib.util
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location("harmonize", os.path.join(HERE, "harmonize.py"))
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)

# The six ANSI slots that carry a hue. 0/7/8/15 are the greys and are asserted
# separately to be untouched.
CHROMATIC = ["color%d" % i for i in (1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14)]
NEUTRAL = ["color0", "color7", "color8", "color15"]

# Floor on the tightest pair of hues in the palette. The unharmonized palette
# sits at 26 degrees (blue against cyan), and losing more than about a fifth of
# that is where "spread deliberately wide" stops being true.
MIN_SEPARATION = 20.0

# Round-tripping through 8-bit sRGB moves a hue by up to about half a degree,
# so the drift bound is MAX_SHIFT plus quantisation rather than MAX_SHIFT flat.
QUANTISATION_SLOP = 1.0

# Contrast against the terminal background is a function of lightness, and
# lightness is held exactly — so any change at all is quantisation. Ratios here
# run 5:1 to 15:1, so a fifth of a point is nothing.
MAX_CONTRAST_DRIFT = 0.25


def relative_luminance(rgb):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def arc(a, b):
    return abs((a - b + 180) % 360 - 180)


def hue_of(hexcode):
    return H.to_lch(H.parse_hex(hexcode))[2]


def main():
    backgrounds = sorted(
        os.path.join(REPO, "backgrounds", f)
        for f in os.listdir(os.path.join(REPO, "backgrounds"))
        if f.endswith(".png")
    )
    if not backgrounds:
        print("no wallpapers found", file=sys.stderr)
        return 2

    bg = H.parse_hex(H.NEUTRALS["background"])
    base_hues = {k: hue_of(H.BASE[k]) for k in CHROMATIC}
    baseline = min(arc(base_hues["color%d" % i], base_hues["color%d" % j])
                   for i, j in itertools.combinations((1, 2, 3, 4, 5, 6), 2))

    failures = []
    print(f"unharmonized palette: tightest pair {baseline:.1f} deg")
    print(f"{'wallpaper':<26} {'hue':>5} {'tightest':>9} {'max drift':>10} {'max dC':>7}")

    for path in backgrounds:
        palette, target = H.derive(path)
        name = os.path.basename(path)

        hues = [hue_of(palette["color%d" % i]) for i in (1, 2, 3, 4, 5, 6)]
        tightest = min(arc(a, b) for a, b in itertools.combinations(hues, 2))
        drift = max(arc(hue_of(palette[k]), base_hues[k]) for k in CHROMATIC)
        d_contrast = max(abs(contrast(H.parse_hex(palette[k]), bg)
                             - contrast(H.parse_hex(H.BASE[k]), bg)) for k in H.BASE)

        print(f"{name:<26} {target:5.0f} {tightest:9.1f} {drift:10.1f} {d_contrast:7.2f}")

        if tightest < MIN_SEPARATION:
            failures.append(f"{name}: hues collapsed to {tightest:.1f} deg apart "
                            f"(floor {MIN_SEPARATION})")
        if drift > H.MAX_SHIFT + QUANTISATION_SLOP:
            failures.append(f"{name}: a hue moved {drift:.1f} deg, past MAX_SHIFT "
                            f"{H.MAX_SHIFT}")
        if d_contrast > MAX_CONTRAST_DRIFT:
            failures.append(f"{name}: contrast against the background moved by "
                            f"{d_contrast:.2f}, so lightness was not held")
        for k in NEUTRAL:
            if palette[k] != H.BASE[k]:
                failures.append(f"{name}: {k} is a grey and was changed to {palette[k]}")

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print(f"OK — {len(backgrounds)} wallpapers: no hue moved past {H.MAX_SHIFT} deg, "
          f"none collapsed below {MIN_SEPARATION} deg, contrast held, greys untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())

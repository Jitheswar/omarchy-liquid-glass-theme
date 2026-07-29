"""Generate dark 'liquid glass' wallpapers.

The theme's surfaces carry no hue any more, so the wallpaper is the only place
colour comes from. That puts two demands on it. It has to stay dark, because a
translucent panel laid on top has to stay readable. And it has to have large,
smooth *structure* — a panel over a flat field looks like a sticker, while a
panel over something that curves reads as glass resting on glass.

The first attempt drove everything from turbulence and came out looking like
choppy water: lots of high-frequency detail, no big forms, and too light to lay
anything on. This builds the forms explicitly instead — a few broad ribbons,
blurred hard, with thin bright arcs riding their crests where light would catch
a curved edge. Noise is left to do one job only, which is breaking up banding.
"""

import math, random


def _ribbon(seed, y, amp, thick, w=1920):
    """A broad horizontal band with a lazy sine wobble, as a closed path."""
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    fr = rnd.uniform(1.1, 1.9)
    top, bot = [], []
    steps = 14
    for i in range(steps + 1):
        x = w * i / steps
        t = (i / steps) * fr * 6.28 + ph
        yy = y + math.sin(t) * amp + math.sin(t * 0.47 + 1.3) * amp * 0.45
        top.append((x, yy))
        bot.append((x, yy + thick))
    d = f"M{top[0][0]:.0f},{top[0][1]:.0f} "
    d += " ".join(f"L{x:.0f},{yy:.0f}" for x, yy in top[1:])
    d += " " + " ".join(f"L{x:.0f},{yy:.0f}" for x, yy in reversed(bot))
    return d + " Z", top


def wallpaper(seed, deep, mid, bright, w=3840, h=2160):
    rnd = random.Random(seed)
    ribbons, arcs, bokeh = [], [], []

    for i, (y, amp, thick, op) in enumerate(
            [(250, 120, 300, 0.85), (560, 150, 380, 1.0), (880, 110, 320, 0.75)]):
        d, crest = _ribbon(seed + i * 13, y, amp, thick)
        ribbons.append(f'<path d="{d}" fill="url(#g{i})" opacity="{op}"/>')
        # specular arc riding the crest of each ribbon
        pts = " ".join(f"L{x:.0f},{yy:.0f}" for x, yy in crest[1:])
        arcs.append(
            f'<path d="M{crest[0][0]:.0f},{crest[0][1]:.0f} {pts}" fill="none" '
            f'stroke="url(#s{i})" stroke-width="{rnd.choice([14,20,26])}" '
            f'stroke-linecap="round"/>')

    for _ in range(7):
        cx, cy = rnd.uniform(0, 1920), rnd.uniform(0, 1080)
        r = rnd.uniform(26, 88)
        bokeh.append(
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="none" '
            f'stroke="#ffffff" stroke-opacity="{rnd.uniform(0.05,0.13):.2f}" '
            f'stroke-width="{rnd.uniform(1.2,2.6):.1f}"/>')

    grads = "\n".join(
        f'''    <linearGradient id="g{i}" x1="0" y1="0" x2="{0.6 + 0.2*i}" y2="1">
      <stop offset="0"   stop-color="{bright}" stop-opacity="0.40"/>
      <stop offset="0.4" stop-color="{mid}"    stop-opacity="0.62"/>
      <stop offset="1"   stop-color="{deep}"   stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="s{i}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"    stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="0.25" stop-color="#ffffff" stop-opacity="{0.50 - 0.08*i}"/>
      <stop offset="0.55" stop-color="{bright}" stop-opacity="{0.62 - 0.10*i}"/>
      <stop offset="1"    stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>''' for i in range(3))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
     viewBox="0 0 1920 1080">
  <defs>
{grads}
    <radialGradient id="glow" cx="0.42" cy="0.40" r="0.75">
      <stop offset="0"   stop-color="{mid}"  stop-opacity="0.30"/>
      <stop offset="0.6" stop-color="{deep}" stop-opacity="0.12"/>
      <stop offset="1"   stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vig" cx="0.5" cy="0.44" r="0.82">
      <stop offset="0"    stop-color="#000000" stop-opacity="0"/>
      <stop offset="0.52" stop-color="#000000" stop-opacity="0.34"/>
      <stop offset="1"    stop-color="#000000" stop-opacity="0.80"/>
    </radialGradient>
    <filter id="soft" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="58"/>
    </filter>
    <filter id="crisp" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="17"/>
    </filter>
    <filter id="bok" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="4"/>
    </filter>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="1" seed="{seed}"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
  </defs>

  <rect width="1920" height="1080" fill="{deep}"/>
  <rect width="1920" height="1080" fill="url(#glow)"/>

  <g filter="url(#soft)">
{chr(10).join("    " + r for r in ribbons)}
  </g>
  <g filter="url(#crisp)" opacity="0.9">
{chr(10).join("    " + a for a in arcs)}
  </g>
  <g filter="url(#bok)">
{chr(10).join("    " + b for b in bokeh)}
  </g>

  <rect width="1920" height="1080" fill="url(#vig)"/>
  <rect width="1920" height="1080" filter="url(#grain)" opacity="0.022"/>
</svg>
'''


FAMILY = [
    ("1-glass-jade",     11, "#03100B", "#125642", "#8FE7C6"),
    ("2-glass-abyss",    23, "#02070F", "#0F3D72", "#7CC4F5"),
    ("3-glass-amethyst", 37, "#09040F", "#3B1A6B", "#B79AEC"),
    ("4-glass-ember",    53, "#100503", "#63260C", "#F0A868"),
    ("5-glass-graphite", 71, "#060709", "#252B33", "#A7AFB8"),
    ("6-glass-rose",     89, "#100309", "#5C1739", "#F094BC"),
]

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1]
    only = sys.argv[2] if len(sys.argv) > 2 else None
    os.makedirs(out, exist_ok=True)
    for name, seed, deep, mid, bright in FAMILY:
        if only and only not in name:
            continue
        open(os.path.join(out, name + ".svg"), "w").write(
            wallpaper(seed, deep, mid, bright))
        print("wrote", name + ".svg")

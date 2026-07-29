"""Generate hueless 'liquid glass' folder icons.

The whole point is that the icon has no colour of its own — it is white and
black at low alpha only, so it takes the hue of whatever sits behind it. The
hard part is staying visible on *both* light and dark backdrops, which is
solved the way real glass solves it: a bright rim and specular catch the light
on a dark background, and a dark underside plus a drop shadow give it an edge
on a light one. At least one of the two is always doing the work.
"""

def folder(glyph=""):
    tab_y = 15
    top = 23
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <defs>
    <!-- Body. Brightest where the sheet curves up to meet the light, thinning
         through the middle where it is most transparent, picking up again at
         the base where it thickens. -->
    <linearGradient id="body" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"    stop-color="#ffffff" stop-opacity="0.26"/>
      <stop offset="0.42" stop-color="#ffffff" stop-opacity="0.09"/>
      <stop offset="0.82" stop-color="#ffffff" stop-opacity="0.07"/>
      <stop offset="1"    stop-color="#ffffff" stop-opacity="0.15"/>
    </linearGradient>
    <!-- The tab sits behind the face, so it reads slightly denser. -->
    <linearGradient id="tabg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.30"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0.13"/>
    </linearGradient>
    <!-- Rim: bright along the top where light lands, falling away down the
         sides. This is what makes it read as a cut edge rather than a shape. -->
    <linearGradient id="rimg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"    stop-color="#ffffff" stop-opacity="0.75"/>
      <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.30"/>
      <stop offset="1"    stop-color="#ffffff" stop-opacity="0.42"/>
    </linearGradient>
    <!-- Specular sweep across the upper left, the single brightest thing. -->
    <linearGradient id="spec" x1="0" y1="0" x2="0.5" y2="1">
      <stop offset="0"   stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="0.6" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="1"   stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <!-- Drop shadow, so the icon still has an edge on a white background. -->
    <filter id="drop" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="1.6" stdDeviation="1.8"
                    flood-color="#000000" flood-opacity="0.55"/>
    </filter>
    <clipPath id="face">
      <path d="M4 {top} h56 a4 4 0 0 1 4 4 v21 a5 5 0 0 1 -5 5 H5 a5 5 0 0 1 -5 -5 V{top+4} a4 4 0 0 1 4 -4 z"/>
    </clipPath>
  </defs>

  <g filter="url(#drop)">
    <!-- back tab -->
    <path d="M7 {tab_y} h15 l5 6 h30 a4 4 0 0 1 4 4 v5 H7 z" fill="url(#tabg)"/>
    <path d="M7 {tab_y} h15 l5 6 h30 a4 4 0 0 1 4 4 v5"
          fill="none" stroke="#ffffff" stroke-opacity="0.34" stroke-width="1"/>

    <!-- face -->
    <path d="M4 {top} h56 a4 4 0 0 1 4 4 v21 a5 5 0 0 1 -5 5 H5 a5 5 0 0 1 -5 -5 V{top+4} a4 4 0 0 1 4 -4 z"
          fill="url(#body)"/>

    <g clip-path="url(#face)">
      <!-- specular sweep -->
      <path d="M0 {top} h34 L14 {top+30} H0 z" fill="url(#spec)"/>
      <!-- shaded underside: what keeps it visible on a light backdrop -->
      <path d="M0 {top+20} h64 v11 H0 z" fill="#000000" fill-opacity="0.20"/>
      <path d="M0 {top+28.4} h64" stroke="#000000" stroke-opacity="0.30" stroke-width="1.4"/>
      {glyph}
    </g>

    <!-- rim -->
    <path d="M4 {top} h56 a4 4 0 0 1 4 4 v21 a5 5 0 0 1 -5 5 H5 a5 5 0 0 1 -5 -5 V{top+4} a4 4 0 0 1 4 -4 z"
          fill="none" stroke="url(#rimg)" stroke-width="1.15"/>
    <!-- hard specular line riding the very top edge -->
    <path d="M6 {top+1.1} h52" fill="none" stroke="#ffffff" stroke-opacity="0.85"
          stroke-width="1.1" stroke-linecap="round"/>
  </g>
</svg>
'''

GLYPHS = {
    "folder": "",
    "folder-documents":
        '<g fill="#ffffff" fill-opacity="0.55">'
        '<rect x="26" y="32" width="12" height="1.7" rx="0.85"/>'
        '<rect x="26" y="36" width="12" height="1.7" rx="0.85"/>'
        '<rect x="26" y="40" width="8"  height="1.7" rx="0.85"/></g>',
    "folder-download":
        '<g fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1.9" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M32 31 v9"/><path d="M27.5 36 l4.5 4.5 l4.5 -4.5"/>'
        '<path d="M26 44 h12"/></g>',
    "folder-music":
        '<g fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1.9" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M30 43 V32 l8 -2 v11"/></g>'
        '<g fill="#ffffff" fill-opacity="0.6">'
        '<circle cx="28" cy="43" r="2.2"/><circle cx="36" cy="41" r="2.2"/></g>',
    "folder-pictures":
        '<g fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1.8">'
        '<rect x="25" y="31" width="14" height="11" rx="2"/></g>'
        '<g fill="#ffffff" fill-opacity="0.6">'
        '<circle cx="29" cy="35" r="1.6"/>'
        '<path d="M26.5 41.2 l4.5 -4.5 l3.5 3.5 l2.5 -2 l2.5 3 z"/></g>',
    "folder-videos":
        '<g fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1.8">'
        '<rect x="25" y="32" width="14" height="10" rx="2"/></g>'
        '<g fill="#ffffff" fill-opacity="0.6">'
        '<path d="M30.5 35 l5 2.9 l-5 2.9 z"/></g>',
    "user-home":
        '<g fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1.9" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M25.5 37 L32 31 l6.5 6"/><path d="M27.5 38.5 V44 h9 v-5.5"/></g>',
}

# Names file managers ask for that are the same drawing under another label.
# folder-open is in here deliberately: an open folder in this material would
# have to be a *different shape*, and a shape with a gaping front is exactly
# where a hueless glass icon stops being legible — there is no fill left to
# carry the rim. Same icon is the better answer than a worse one.
ALIASES = (
    ("folder-open", "folder"),
    ("folder-downloads", "folder-download"),
    ("folder-video", "folder-videos"),
    ("folder-image", "folder-pictures"),
    ("folder-images", "folder-pictures"),
    ("folder-document", "folder-documents"),
    ("folder-publicshare", "folder"),
    ("folder-templates", "folder"),
    ("folder-remote", "folder"),
    ("folder-visiting", "folder"),
    ("folder-desktop", "folder"),
    ("inode-directory", "folder"),
    # The three below were the last coloured folders on the desktop. Yaru ships
    # each of them as a colour-variant icon, so with nothing here they fell
    # through to the inherited prussian-green set and sat next to the glass
    # ones. user-desktop is the freedesktop icon-naming spec name for the
    # Desktop folder — folder-desktop above is a guess nothing actually asks
    # for, and is kept only because it costs nothing.
    ("user-desktop", "folder"),
    ("folder-new", "folder"),
    # Shown while a drag hovers a drop target. Yaru uses an open folder for
    # this; an open folder in a hueless material has no fill left to carry the
    # rim, so it borrows the download glyph instead — an arrow going into a
    # folder is the same reading and stays in the material. It never appears
    # beside a real Downloads folder, so the collision does not cost anything.
    ("folder-drag-accept", "folder-download"),
)

if __name__ == "__main__":
    import os
    import sys

    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)

    written = 0
    for name, glyph in list(GLYPHS.items()) + [(a, GLYPHS[src]) for a, src in ALIASES]:
        with open(os.path.join(out, name + ".svg"), "w") as f:
            f.write(folder(glyph))
        written += 1

    print("wrote", written, "svg files to", out)

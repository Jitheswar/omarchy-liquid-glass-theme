# Liquid Glass icons

Folder icons only. Everything else falls through to the inherited theme, so
this stays small and does not have to keep up with Yaru.

The folders carry no hue. They are white and black at low alpha, which is what
lets them sit on any background and take its colour — the same principle the
theme's surfaces use. Staying visible on both light and dark backdrops is the
whole difficulty, and it is solved the way glass solves it: a bright rim and a
specular catch the light on a dark background, while a shaded underside and a
drop shadow give it an edge on a light one. At least one is always working.

Regenerate with:

    python3 generate.py scalable/places

Install (what `omarchy theme set` does not do for you):

    cp -r . ~/.local/share/icons/LiquidGlass
    gtk-update-icon-cache -f ~/.local/share/icons/LiquidGlass

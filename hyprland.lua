-- Liquid Glass — Hyprland window material (Omarchy 4 port).
--
-- This file carries everything a theme cannot reach through shell.toml: the
-- window decoration (blur, squircle rounding, glow rim, shadows), the per-app
-- window opacity, and the layer rules that let the translucent quickshell
-- surfaces blur what is behind them.
--
-- Named hyprland.lua so Omarchy stages it into current/theme/hyprland.lua and
-- loads it automatically, at the end of `default.hypr.omarchy` via
-- `require_optional.module("omarchy.current.theme.hyprland")`. That means it
-- runs AFTER the Hyprland defaults and the default window rules — so the
-- opacity and decoration below win — and with the `o` helper in scope (it is
-- defined by default.hypr.helpers before this module is required).
--
-- The material is deliberately *clear*, not frosted. Frost is diffusion: many
-- blur passes plus grain, which hides whatever is behind it. This aims at the
-- other thing — thick, lit glass you can almost see through, where the edge
-- does the work instead of the surface.

-- The rim is a bevel, not a frame. 90deg so it runs bright at the top and
-- falls away to near-black at the base, which is how a curved edge reads under
-- a single overhead light. Same gradient feeds the shell surfaces via
-- shell.toml's [hyprland] tokens, so a window and a panel agree about the
-- light source.
local activeBorderColor = {
  colors = {
    "rgba(FFFFFFF2)",
    "rgba(FFFFFF99)",
    "rgba(80808066)",
    "rgba(000000CC)",
  },
  angle = 90,
}
local inactiveBorderColor = {
  colors = { "rgba(FFFFFF2E)", "rgba(00000066)" },
  angle = 90,
}

hl.config({
  general = {
    col = {
      active_border = activeBorderColor,
      inactive_border = inactiveBorderColor,
    },

    -- Glass needs room to read as a separate pane, not a tiled sheet.
    gaps_in  = 6,
    gaps_out = 14,

    -- 3px so the bevel gradient can actually read as a lens edge. At 1-2px it
    -- collapses into a plain outline.
    border_size = 3,
  },

  group = {
    col = {
      border_active = activeBorderColor,
      border_inactive = inactiveBorderColor,
      border_locked_active = activeBorderColor,
      border_locked_inactive = inactiveBorderColor,
    },

    groupbar = {
      col = {
        active = "rgba(FFFFFF4D)",
        inactive = "rgba(00000073)",
      },
      text_color = "rgb(EDEDED)",
      text_color_inactive = "rgba(E0E0E099)",

      -- The groupbar was the one surface still drawing opaque, and the alphas
      -- above are why it was easy to miss: the colours are already alpha
      -- values, so the tabs *look* translucent in the config but composite
      -- over nothing. A groupbar is not a window and does not inherit window
      -- blur, so it needs this explicitly.
      blur = true,

      -- The tab's visible shape is drawn by gradient_rounding; sweeping the
      -- other three rounding knobs changed nothing measurable (see upstream
      -- README), so only this one is set.
      gradient_rounding = 10,
    },
  },

  decoration = {
    -- 20 is Hyprland's ceiling. rounding_power well above 2 turns the corner
    -- into a superellipse — continuous curvature rather than a circular arc
    -- pasted onto a straight edge. The quickshell shell reads this same value
    -- and inherits the radius on its panels.
    rounding       = 20,
    rounding_power = 4.5,

    -- Fully opaque at the compositor level. Transparency is supplied per-app
    -- by window opacity below (terminals keep 1.0 and use their own
    -- background alpha, keeping glyphs solid).
    active_opacity   = 1.0,
    inactive_opacity = 1.0,

    dim_inactive = true,
    dim_strength = 0.06,
    dim_special  = 0.35,

    blur = {
      enabled = true,

      -- Low and few, on purpose. This is the single biggest difference from a
      -- frosted theme: at size 4 / 3 passes you can still make out the shapes
      -- behind the pane, so it reads as something you are looking *through*
      -- rather than a fogged panel.
      size   = 4,
      passes = 3,

      -- Menus, dropdowns and tooltips have to be glass too.
      popups             = true,
      popups_ignorealpha = 0.2,
      special            = true,

      -- An input method's candidate window — fcitx5, ibus — is neither a
      -- popup nor a layer, so `popups` and the layerrules below do not reach
      -- it. Cost nothing with no IME running.
      input_methods             = true,
      input_methods_ignorealpha = 0.2,

      -- Glass is *lit* — brighter and more saturated than what sits behind it,
      -- not a grey veil. brightness lifts the pane off the wallpaper;
      -- vibrancy is what makes colour bleed through as refraction.
      brightness        = 1.18,
      contrast          = 1.18,
      vibrancy          = 0.80,
      vibrancy_darkness = 0.45,

      -- Near zero. Grain is what the eye reads as "frosted"; clear glass has
      -- none. Just enough left to stop the wallpaper's gradients banding.
      noise = 0.003,

      new_optimizations = true,

      -- Load-bearing for the window-opacity rules below: without it, blur
      -- strength would follow window alpha down exactly where it is supposed
      -- to be doing the work.
      ignore_opacity = true,

      -- Off on purpose: seeing *other windows* refracted behind the front one
      -- is the layered depth this theme is built around.
      xray = false,
    },

    -- The inner rim. Hyprland calls this "glow" and the name misleads: it is
    -- not an outer bloom but an *inner* one — the shader measures distance from
    -- the window's edge and fades a colour inward over `range`, following the
    -- same rounding_power the corner uses. White at low alpha on a 90deg
    -- gradient: lit at the top, near nothing at the base. No hue, so the rim
    -- takes its colour from whatever the blur behind it is carrying.
    --
    -- render_power shapes the falloff (pow(1 - dist/range, power)); 14/2 is the
    -- pair that ramps instead of spiking into a doubled outline.
    glow = {
      enabled = true,
      range = 14,
      render_power = 2,
      color = { colors = { "rgba(FFFFFF47)", "rgba(FFFFFF0F)" }, angle = 90 },
      color_inactive = { colors = { "rgba(FFFFFF1A)", "rgba(FFFFFF00)" }, angle = 90 },
    },

    -- Tight and close, not a halo. A cast shadow is not evenly dark: the light
    -- overhead is occluded most directly under the bottom edge, so it is a
    -- gradient on the same 90deg as the border and rim — three effects now
    -- agreeing about where the light is.
    shadow = {
      enabled      = true,
      range        = 18,
      render_power = 4,
      color = { colors = { "rgba(00000038)", "rgba(00000085)" }, angle = 90 },
      color_inactive = { colors = { "rgba(00000020)", "rgba(00000050)" }, angle = 90 },
      offset = "0 3",
      scale  = 0.95,
    },

    -- The liquid half of the name. Shipped OFF: motion blur engages only while
    -- a window is moving, but the first machines to enable it reported flicker
    -- while dragging. `samples` is quality against GPU cost (7 default, 64
    -- ceiling; 12 is smooth on a 1080p laptop panel). Set enabled = true here
    -- if your hardware likes it.
    motion_blur = {
      enabled = false,
      samples = 12,
    },
  },
})

-- ── Motion ────────────────────────────────────────────────────────────────
-- A pane that size has to settle when it arrives and get out of the way when
-- dismissed, so the two directions are deliberately not symmetrical.
hl.curve("glassSettle",  { type = "bezier", points = { { 0.16, 1.0 }, { 0.3, 1.0 } } })
hl.curve("glassDismiss", { type = "bezier", points = { { 0.42, 0.0 }, { 1.0, 1.0 } } })

hl.animation({ leaf = "layersIn",  enabled = true, speed = 3.5, bezier = "glassSettle",  style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2.0, bezier = "glassDismiss", style = "fade" })

-- ── Window transparency ───────────────────────────────────────────────────
-- Two mechanisms, because apps fall into two camps.
--
-- Terminals can render a translucent *background* while keeping glyphs fully
-- opaque (one of alacritty/foot/ghostty/kitty sets its own background alpha
-- from colors.toml). They want no window opacity stacked on top.
o.window({ tag = "terminal" }, { opacity = "1.0 1.0" })

-- Everything else — GTK, Electron, browsers — draws an opaque background and
-- exposes no equivalent knob. The only lever is window opacity, which fades
-- text along with the background, so it is kept mild: 0.92 active / 0.90
-- inactive is enough that the blur behind registers as glass without a page
-- becoming hard to read. Blur still applies because ignore_opacity is on.
--
-- Media apps keep their own rules in Omarchy's default/hypr/apps that strip
-- the default-opacity tag, so video stays fully opaque for free.
o.window({ tag = "default-opacity" }, { opacity = "0.92 0.90" })

-- ── Shell surfaces ────────────────────────────────────────────────────────
-- Each Omarchy-4 quickshell surface is a translucent layer. `blur on` lets the
-- wallpaper show through as glass, and `ignore_alpha` keeps the clear margin
-- around a floating surface from being blurred along with it. The thresholds
-- are low because these panels are genuinely transparent.
--
-- omarchy-menu covers the launcher, main menu, and their flyouts; it carries
-- a bigger drop shadow than the bar, so its ignore_alpha sits higher (0.35)
-- to keep the shadow ring from picking up the blur's brightness/vibrancy.
hl.layer_rule({ match = { namespace = "omarchy-bar" },           blur = true, blur_popups = true, ignore_alpha = 0.04 })
hl.layer_rule({ match = { namespace = "omarchy-menu" },          blur = true, ignore_alpha = 0.35 })
hl.layer_rule({ match = { namespace = "omarchy-notifications" }, blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-osd" },           blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-clipboard" },     blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-emojis" },        blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-image-selector" }, blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-keyboard-panel" }, blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-polkit" },         blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-reminders" },      blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-speed-test" },     blur = true, ignore_alpha = 0.06 })

-- Liquid Glass — Hyprland (Omarchy 4.0)
--
-- Converted from the 3.8-era hyprland.conf. Omarchy 4.0 auto-loads this file
-- from the active theme (require_optional "omarchy.current.theme.hyprland"),
-- after the stock app rules and before the user's looknfeel.lua — so window
-- rules here win over defaults, while anything the user sets in their own
-- looknfeel.lua still wins over this.
--
-- The material is deliberately *clear*, not frosted. Frost is diffusion: many
-- blur passes plus grain, which hides whatever is behind it. This aims at the
-- other thing — thick, lit glass you can almost see through, where the edge
-- does the work instead of the surface.

local activeBorderColor = {
	colors = { "rgba(fffffff2)", "rgba(ffffff99)", "rgba(80808066)", "rgba(000000cc)" },
	angle = 90,
}
local inactiveBorderColor = {
	colors = { "rgba(ffffff2e)", "rgba(00000066)" },
	angle = 90,
}

hl.config({
	-- The rim is a bevel, not a frame: bright at the top, falling to near-black
	-- at the bottom, the way a curved edge reads under a single overhead light.
	general = {
		col = {
			active_border = activeBorderColor,
			inactive_border = inactiveBorderColor,
		},

		-- Glass needs room to read as a separate pane, not a tiled sheet.
		gaps_in = 6,
		gaps_out = 14,

		-- 3px so the bevel gradient has enough room to read as a lens edge.
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
				active = "rgba(ffffff4d)",
				inactive = "rgba(00000073)",
			},
			text_color = "rgb(ededed)",
			text_color_inactive = "rgba(e0e0e099)",

			-- A groupbar is not a window and does not inherit window blur; this
			-- is what makes the alphas above mean something.
			blur = true,

			gradient_rounding = 10,
		},
	},

	decoration = {
		-- Superellipse corners (rounding_power > 2): continuous curvature rather
		-- than a circular arc pasted onto a straight edge.
		rounding = 20,
		rounding_power = 4.5,

		-- Fully opaque at the compositor level; transparency is per-app so
		-- glyphs stay solid.
		active_opacity = 1.0,
		inactive_opacity = 1.0,

		-- Barely there. Heavy dimming reads as "disabled"; real glass just sits
		-- slightly further away.
		dim_inactive = true,
		dim_strength = 0.06,
		dim_special = 0.35,

		blur = {
			-- Low and few, on purpose: at size 4 / 3 passes you can still make
			-- out the shapes behind the pane. Raising to ~8/4 turns it frost.
			size = 4,
			passes = 3,
			enabled = true,

			-- Menus, dropdowns, tooltips, special workspaces and IME candidate
			-- windows have to be glass too, or they punch opaque holes through
			-- the effect.
			popups = true,
			popups_ignorealpha = 0.2,
			special = true,
			input_methods = true,
			input_methods_ignorealpha = 0.2,

			-- Glass is *lit*: brightness lifts the pane off the wallpaper,
			-- vibrancy lets colour bleed through as refraction rather than
			-- washing out to grey.
			brightness = 1.18,
			contrast = 1.18,
			vibrancy = 0.80,
			vibrancy_darkness = 0.45,

			-- Near zero: grain is what the eye reads as "frosted". Just enough
			-- to stop wide gradients banding.
			noise = 0.003,

			new_optimizations = true,

			-- Load-bearing for the window-opacity rules below: blur strength
			-- must not follow window alpha down.
			ignore_opacity = true,

			-- Off on purpose: seeing other windows refracted behind the front
			-- one is the layered depth this theme is built around.
			xray = false,
		},

		-- The inner rim. Not an outer bloom: the shader fades light inward from
		-- the window's edge over `range`, following the superellipse — the real
		-- thing every GTK surface in this theme can only imitate with
		-- `inset 0 1px 0`. White at low alpha on a 90deg gradient, no hue, so
		-- the rim takes its colour from whatever the blur carries.
		glow = {
			enabled = true,
			range = 14,
			render_power = 2,
			color = { colors = { "rgba(ffffff47)", "rgba(ffffff0f)" }, angle = 90 },
			color_inactive = { colors = { "rgba(ffffff1a)", "rgba(ffffff00)" }, angle = 90 },
		},

		-- Tight and close, not a halo. Gradient colour needs 0.56; same 90deg
		-- overhead source as the border and the rim above.
		shadow = {
			enabled = true,
			range = 18,
			render_power = 4,
			color = { colors = { "rgba(00000038)", "rgba(00000085)" }, angle = 90 },
			color_inactive = { colors = { "rgba(00000020)", "rgba(00000050)" }, angle = 90 },
			offset = "0 3",
			scale = 0.95,
		},

		motion_blur = {
			-- On a theme named liquid glass it is tempting; it stays off because
			-- it cannot be judged at rest and costs nothing while static.
			enabled = false,
			samples = 12,
		},
	},
})

-- ── Motion ────────────────────────────────────────────────────────────────
-- Only layers are touched: a pane that size has to settle when it arrives and
-- get out of the way when dismissed. Everything else keeps the Omarchy curve.

hl.curve("glassSettle", { type = "bezier", points = { { 0.16, 1.0 }, { 0.3, 1.0 } } })
hl.curve("glassDismiss", { type = "bezier", points = { { 0.42, 0.0 }, { 1.0, 1.0 } } })

hl.animation({ leaf = "layersIn", enabled = true, speed = 3.5, bezier = "glassSettle", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2, bezier = "glassDismiss", style = "fade" })

-- ── Window transparency ───────────────────────────────────────────────────
-- Terminals render a translucent background with solid glyphs (their configs
-- ship background alpha), so they want no window opacity stacked on top.
o.window({ tag = "terminal" }, { opacity = "1.0 1.0" })

-- Everything else draws an opaque background; window opacity is the only
-- lever, kept mild. Blur still applies underneath because blur:ignore_opacity
-- is on. Later rules win: these intentionally override the stock browser
-- opacity rules that loaded earlier.
o.window({ tag = "default-opacity" }, { opacity = "0.92 0.90" })
o.window({ tag = "chromium-based-browser" }, { opacity = "0.92 0.90" })
o.window({ tag = "firefox-based-browser" }, { opacity = "0.92 0.90" })

-- ── Shell surfaces ────────────────────────────────────────────────────────
-- Omarchy 4.0's Quickshell shell replaces waybar/walker/mako/swayosd; these
-- are its layer namespaces. Each panel is glass, and ignore_alpha keeps the
-- clear margin around a floating surface from being blurred along with it.
--
-- The launcher's threshold is higher (0.35) because its drop shadow paints a
-- ring of semi-transparent pixels well beyond the panel; blurring that ring
-- produced a saturated halo shaped like the layer rectangle, not the panel.

hl.layer_rule({ match = { namespace = "omarchy-bar" }, blur = true, ignore_alpha = 0.04, blur_popups = true })
hl.layer_rule({ match = { namespace = "omarchy-menu" }, blur = true, ignore_alpha = 0.35 })
hl.layer_rule({ match = { namespace = "omarchy-notifications" }, blur = true, ignore_alpha = 0.06 })
hl.layer_rule({ match = { namespace = "omarchy-osd" }, blur = true, ignore_alpha = 0.06 })

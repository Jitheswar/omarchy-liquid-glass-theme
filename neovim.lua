-- Liquid Glass — Neovim
--
-- aether.nvim takes an explicit colour table, so the editor gets the exact
-- same palette as the rest of the desktop rather than an approximation.
-- transparent = true is deliberate: the terminal's own frosted background
-- shows through, so the editor reads as one more pane of glass instead of
-- punching an opaque rectangle through the effect.

return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      transparent = true,
      colors = {
        bg         = "#0A0A0A",
        dark_bg    = "#0A0A0A",
        darker_bg  = "#050505",
        lighter_bg = "#1A1A1A",
        -- Neutral, like selection_background in colors.toml, and dark rather
        -- than the light grey that file uses: this one is a *background* under
        -- unchanged foreground text, not a highlight with its own text colour.
        -- It also lands on LspReference* below, which paints every occurrence
        -- of the symbol under the cursor, so it has to stay quiet.
        selection  = "#2E2E2E",

        fg         = "#E0E0E0",
        dark_fg    = "#C6C6C6",
        bright_fg  = "#F2F2F2",
        muted      = "#6E6E6E",

        red        = "#F2798F",
        orange     = "#EFAE8C",
        yellow     = "#E5CE8A",
        green      = "#6FBF7A",
        cyan       = "#74C7CE",
        blue       = "#6FB6D6",
        purple     = "#B49BE0",
        -- Was #CBD8D2, which is a pale mint rather than a brown — the last of
        -- the jade cast. Neutralised at the same lightness instead of being
        -- given a hue it never had: aether uses this slot for very little, and
        -- inventing a tan here would spread the palette for no reading.
        brown      = "#D2D2D2",

        bright_red    = "#FF97A8",
        bright_yellow = "#F5E2A8",
        bright_green  = "#8FD895",
        bright_cyan   = "#96DCE2",
        bright_blue   = "#96CFE8",
        bright_purple = "#CBB6F0",
      },
      on_highlights = function(hl, c)
        hl.CursorLine = { bg = c.lighter_bg }
        hl.CursorLineNr = { fg = c.green, bold = true }
        hl.LspReferenceText = { bg = c.selection, fg = c.bright_fg }
        hl.LspReferenceRead = hl.LspReferenceText
        hl.LspReferenceWrite = hl.LspReferenceText
        hl.SnacksPickerDir         = { fg = c.muted }
        hl.SnacksPickerPathHidden  = { fg = c.muted }
        hl.SnacksPickerPathIgnored = { fg = c.muted }
        hl.SnacksPickerListCursorLine = { bg = c.lighter_bg }
      end,
    },
    config = function(_, opts)
      require("aether").setup(opts)
      vim.cmd.colorscheme("aether")
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}

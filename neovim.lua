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
        darker_bg  = "#040807",
        lighter_bg = "#1A1A1A",
        selection  = "#1D4937",

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
        brown      = "#CBD8D2",

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

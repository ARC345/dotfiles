return {
  -- Catppuccin Macchiato to match the KDE desktop theme
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    opts = {
      flavour = "macchiato",
      integrations = {
        cmp = true,
        gitsigns = true,
        treesitter = true,
        telescope = true,
        which_key = true,
        mason = true,
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "catppuccin",
    },
  },
}

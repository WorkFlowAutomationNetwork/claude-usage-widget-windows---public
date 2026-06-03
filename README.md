# Claude Usage Widget

A floating desktop widget for Windows that shows your Claude.ai session and weekly usage in real time.

---

## Requirements

- Windows 10 or 11
- Python 3.10 or later — download from https://www.python.org/downloads/
  - During install, tick **"Add Python to PATH"**

---

## First-time setup

1. Run **`setup.bat`** — installs the required Python packages (one-time only)
2. Run **`launch.bat`** — starts the widget

---

## Daily use

Double-click **`launch.bat`** to start. The widget appears in the top-left corner and a green dot appears in your system tray.

**Tray menu** (right-click the green dot):
| Option | What it does |
|--------|-------------|
| Show / Hide | Toggle the floating window |
| Refresh now | Force an immediate data fetch |
| Theme | Switch between Default, Neon, Light, Minimal |
| Set session key… | Update your Claude session key |
| Quit | Exit cleanly |

Only one instance runs at a time — launching again when it's already running does nothing.

---

## Getting your session key

1. Open [claude.ai](https://claude.ai) in Chrome and log in
2. Press **F12** → **Application** tab → **Cookies** → `https://claude.ai`
3. Find the cookie named `sessionKey` and copy its value
4. Paste it into the widget when prompted (or via Tray → Set session key…)

Your key is stored locally in `~/.claude/claude-usage-widget.json` and never sent anywhere other than the Claude API.

---

## Auto-start with Windows

To have the widget launch automatically when you log in:

1. Press **Win + R**, type `shell:startup`, press Enter
2. Create a shortcut to `launch.bat` in the folder that opens

---

## Troubleshooting

**Widget doesn't appear after launching**
The window may be off-screen from a previous session. The app auto-corrects this on startup — if it still doesn't appear, check the system tray for the green dot and use Show / Hide.

**Multiple green dots in tray**
Hover over each one — Windows removes icons for dead processes on hover. The single-instance guard prevents this from recurring.

**"No session key" error in the widget**
Use Tray → Set session key… to enter your key.

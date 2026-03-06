#!/usr/bin/env bash
# Skilldex popup: opens a floating terminal with fzf, copies result to clipboard
set -euo pipefail

SKILLDEX="$HOME/.claude/bin/skilldex.sh"

osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    set w to do script "clear && ~/.claude/bin/skilldex.sh | tee /tmp/skilldex-result.txt; if [ -s /tmp/skilldex-result.txt ]; then cat /tmp/skilldex-result.txt | pbcopy; fi; sleep 0.3; exit"
    set current settings of w to settings set "Basic"
    -- Wait for window to appear, then resize
    delay 0.3
    set bounds of front window to {300, 200, 1200, 700}
end tell
APPLESCRIPT

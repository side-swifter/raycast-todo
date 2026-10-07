#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title name
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🪪

printf '%s' 'Akshayraj Sanjai' | pbcopy
sleep 0.15
osascript -e 'tell application "System Events" to keystroke "v" using command down'

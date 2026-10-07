#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title first name
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🪪

printf '%s' 'Akshayraj' | pbcopy
sleep 0.15
osascript -e 'tell application "System Events" to keystroke "v" using command down'

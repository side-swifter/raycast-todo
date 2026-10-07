#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title school
# @raycast.mode silent

# Optional parameters:
# @raycast.icon ✉️

printf '%s' 'asanjai@students.wcpss.net' | pbcopy
sleep 0.15
osascript -e 'tell application "System Events" to keystroke "v" using command down'

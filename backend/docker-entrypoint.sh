#!/bin/sh
set -e
# Virtual display so headful browsers (for bot-protected sites) work on a
# headless server. Headless checks ignore it.
Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp >/dev/null 2>&1 &
export DISPLAY=:99
exec "$@"

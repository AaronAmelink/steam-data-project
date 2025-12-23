#!/bin/bash
set -e

# Export environment variables to /etc/environment for cron jobs
printenv > /etc/environment

# Start cron in the background
cron -f &

# If arguments are provided, run them (like CMD)
if [ $# -gt 0 ]; then
  exec "$@"
else
  # Default behavior: tail cron log
  tail -f /var/log/cron.log
fi

#!/bin/bash
cd /app
/usr/bin/python3 -m pipelines.calculate_playtime.calculate_playtime --cron

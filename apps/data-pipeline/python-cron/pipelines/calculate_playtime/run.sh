#!/bin/bash
cd /app || exit
/usr/bin/python3 -m pipelines.calculate_playtime.calculate_playtime --cron

## Introduction
A mono-repo for the steam data project. Similar to statsforspotify.com, this project aims to track hourly steam player data to provide analytics. Still a work in progress.

To run locally, reference the specific readme.mds in each aspect of the app.

### Stack

- Uses FastAPI / Pydantic for backend w/ Azure SQL Server (Why azure? good free plan)
- Uses cron to run hourly jobs (only need 1/2 jobs, something like celery would be overkill)
- React frontend (not started)

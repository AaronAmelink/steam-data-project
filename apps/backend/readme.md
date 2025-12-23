# Setup


---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- If on windows, WSL2 is recommended

---

## Docker Setup
1. Copy .env.example to .env and modify any necessary environment variables.

   ```bash
   cp .env.example .env
   ```
2. Uncommit out `create_demo_data()` in `source/main.py` if you want demo data to be created on startup. Comment this out after so it does do it every time you start docker.

3. run the following command to start the development environment:
   ```bash
   docker compose --profile local up
   ```
4. The apps.backend server should now be running at `http://localhost:8000`.
5. You can connect to Mongo from VSCode/PyCharm with this string `mongodb://localhost:27017`
6. if you are using PyCharm, make sure to set the python interpreter to the docker container interpreter, and mark `source` as a source root.

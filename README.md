[[_TOC_]]

# App - BACK

## Draft Arborescence:

```
.
|   requirements.txt
|
+-  scripts
|       |   check_requierements.sh
|       |   clean_env.sh
|       |   init_env.sh
|       |   run_task.sh
|       |   version.sh
|       |   ...
|       |
+-      +-  templates
|       |       |   .env.example
|       |       |   create_database.sql.example
|       |       |   docker-compose.example
|       |       |   Dockerfile.example
|       |       |   ...
|
+-  app
|       |   main.py
|       |
|       +-  config
|       |       |   auth.py
|       |       |   database.py
|       |       |   env.py
|       |       |   metadata_tag.py
|       |       |   roles.py
|       |       |   seeds.py
|       |       |   translation.py
|       |       |   ...
|       |       |
|       |       +-   seeds
|       |       |    |  entity.json
|       |
|       +-  enums
|       |       |   enum_type.py
|       |
|       +-  errors
|       |       |   error_type.py
|       |
|       +-  helpers
|       |       |   check.py
|       |       |   router.py
|       |       |   ...
|       |
|       +-  locales
|       |       +-  lang
|       |       |    |  errors.lang.yml
|       |       |    |  models.lang.yml
|       |       |    |  ...
|       |
|       +-  models (orm)
|       |       |   entity_db.py
|       |
|       +-  routers
|       |       |   routes.py
|       |       |
|       |       +-  vX
|       |       |    |  __init__.py
|       |       |    |  route.py
|       |       |
|       |       +-  vY
|       |
|       +-  schemas
|       |       |   entity_class.py
|       |
|       +-  tests
|       |       |   fake.py
|       |       |   test_main.py
|       |       |
|       |       +-  data
|       |       |   |   fake_file.json
|       |       |   |   ...
|       |       +-  routers
|       |       |       +-  vX
|       |       |       |   |   test_route.py
|       |       |
|       |       +-  utils
|       |       |   |   fake.py
|       |       |   |   ...
|       |
|       +-  utils
|       |       |   dependency.py
|       |       |   midddleware.py
|       |       |   tools.py
|       |       |   ...
```

## Installation

*If you are in jetlab, you need to export the path tobe able to use the command install by pip :*
```bash
echo 'export PATH="/config/.local/bin/:$PATH"' >> ~/.zshrc
```

### Create your virtual environment

If you are working on a local machine, make sure you have the correct version of python3.11 and install venv if not already done :
```bash
sudo apt install python3.11
sudo apt install python3.11-venv -y
```

Then create your venv and activate it :
```bash
python3.11 -m venv env
source env/bin/activate
```

### Using the script

You can install all you need with the script `scripts/init_env.sh`.
This script takes an argument depending on what you need.

If you need to run the server localy, run with the parameter `local` :
```bash
./scripts/init_env.sh local
```

If you need to run the server in a docker, run with the parameter `docker` :
```bash
./scripts/init_env.sh docker
```

If you want to run the server by aws, run with the parameter `aws` :
```bash
./scripts/init_env.sh aws
```

### Manually

You can install manually the dependencies. Run those commands :
```bash
pip install boto3
pip install Faker
pip install "fastapi[all]"
pip install pre-commit
pip install pytest
pip install pytest-cov
pip install pytest-check
pip install pytest-dotenv
pip install pytest-mock
pip install python-i18n
pip install sqlalchemy
pip install unidecode
```
Or you can run this command (that will install more libraries) :
```bash
pip install -r requirements.txt
```

### In all cases

If you'll use the git commands, run first :
```bash
pre-commit install
```

## Serveur

### Without docker-compose

If you didn't install by using the script `scripts/init_env.sh`, you need to create a file `.env`. Copy the `scripts/templates/.env.example` then adapt it.
Now you can run the command :
```bash
uvicorn app.main:app --reload
```
### With docker-compose

To run the server the first time you have to init the environnement :
```bash
./scripts/init_env.sh docker
```

Now the server is running. You can use `docker-compose` as usual :
```bash
# to stop the server
docker-compose down

# to start the server
docker-compose up -d

# to restart the server
docker-compose restart
```

## Environnement

You can find the file `scripts/templates/.env.example` to generate the file `.env`.
In this file, you can put those variables (all are optional) :
```bash
# the title on swagger
FASTAPI_TITLE="[FASTAPI_TITLE]"

# required for openapi in jetlab server
ROOT_PATH="/studio/[UID_STUDIO]/proxy/[UVICORN_PORT]/"

# the mode to run fastapi (dev|test)
FASTAPI_ENV=dev

# the database informations - required if you use distant database
DATABASE_ENGINE=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_DB=
DATABASE_PORT=
DATABASE_SERVER=
DATABASE_URL="${DATABASE_ENGINE}://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_SERVER}:${DATABASE_PORT}/${DATABASE_DB}"
```

## Logs

In the file *logging.conf*, you can change the path to logfile and enable logconsole and/or logfile if you wish.

For production and pre-production environments, you must change the log level from DEBUG to INFO.

You can add log with following lines :
```python

# import logger
from fastapi.logger import logger

logger.critical('msg')
logger.debug('msg')
logger.error('msg')
logger.info('msg')
logger.warning('msg')

```

## Tests Unitaires

To run all the test :
```bash
pytest
```
To run the test and get the coverage report :
```bash
pytest -vv --cov=app --cov-report term-missing --cov-report term:skip-covered
```
To run the test and get the coverage report in html mode :
```bash
pytest --cov-report html
```
It's possible to combine :
```bash
pytest -vv --cov=app --cov-report term-missing --cov-report term:skip-covered --cov-report html
```

## Process

[Here is the git workflow](./wiki/git_workflow.md)

[How to code a new feature](./wiki/process_feature.md)

[How to update python](./wiki/update_python.md)

[Documentation](./wiki/documentation.md)

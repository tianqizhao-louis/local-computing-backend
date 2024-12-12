# Local Computing Breeder Service

A simple service for managing breeder data with options for local testing and GCP deployment.

---

## 🚀 Deployment Instructions

### 1. Local Testing Setup

Follow these steps to deploy the service locally:

#### Step 1: Create an `.env` File

Create an environment file to store your configuration variables:

```bash
vim .env
```

#### Step 2: Add the Following Content to .env

```bash
DATABASE_URL=<ENV>
JWT_SECRET_KEY=<ENV>
JWT_ALGORITHM=<ENV>
JWT_REFRESH_SECRET=<ENV>
CAT_API_KEY=<ENV>
```

##### Step 3: Activate Docker on Desktop

run the docker container:

```bash
./build.sh
```

The breeder service will run on http://localhost:8082/api/v1/pets

### 2. Deploy to GCP

#### Option 1. Deploy directly to a VM

##### Step 1: Set up VM on GCP

Create a cloud engine on GCP
SSH into the VM, git clone current repo

##### Step 2: Run directly on VM

To run mannually, please run the following step by step:

```bash
curl -sSL https://install.python-poetry.org | python3 -
cd breeder-service
poetry install --only main

//activate the virtual env poetry created
source /path/for/the/virtual/env/activate
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PIP_NO_CACHE_DIR=off
export PIP_DISABLE_PIP_VERSION_CHECK=on
export PIP_DEFAULT_TIMEOUT=100
export POETRY_VERSION=1.4.1
export POETRY_HOME="/opt/poetry"
export POETRY_VIRTUALENVS_IN_PROJECT=true
export POETRY_NO_INTERACTION=1
export PYSETUP_PATH="/opt/pysetup"
export VENV_PATH="/opt/pysetup/.venv"
export PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
export PYTHONPATH="/app"
export DEP_DATABASE_URI="<ENV>"
export DATABASE_URI="<ENV>"
export URL_PREFIX="<ENV>"
export DB_USER="<ENV>"
export DB_PASS="<ENV>"
export DB_NAME="<ENV>"
export JWT_SECRET_KEY="<ENV>"
export JWT_ALGORITHM="<ENV>"
export JWT_REFRESH_SECRET="<ENV>"
export CAT_API_KEY="<ENV>"
export FASTAPI_ENV="production"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8082
```

Then the breeder service will run on http://external-ipv4:8082/api/v1/pets

#### Option 2. Deploy through docker container

##### Step 1: Step 1: Create an `prod.env` File

Create an environment file to store your configuration variables:

```bash
vim prod.env
```

##### Step 2: Add the Following Content to prod.env

```bash
DEP_DATABASE_URI=<ENV>
//Change URL_PREFIX to your corresponding ipv4
URL_PREFIX=<ENV>
DATABASE_URI=<ENV>

DB_USER=<ENV>
DB_PASS=<ENV>
DB_NAME=<ENV>
INSTANCE_UNIX_SOCKET=<ENV>
INSTANCE_CONNECTION_NAME=<ENV>
JWT_SECRET_KEY=<ENV>
JWT_ALGORITHM=<ENV>
JWT_REFRESH_SECRET=<ENV>
CAT_API_KEY=<ENV>

```

##### Step 3: Activate Docker on Desktop

run the docker container:

```bash
docker-compose -f docker-compose.prod.yml --env-file prod.env up --build -d
```

The breeder service will run on http://external-ipv4:8082/api/v1/pets

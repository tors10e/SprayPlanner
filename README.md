# SprayPlanner

Application designed to determine what vineyard and orchard sprays to purchase based on growth stages, disease risks, and chemical constraints. It includes a Flask REST API backend, a React frontend for database management, and supports both SQLite (for simple local use) and a standalone PostgreSQL database for test and production environments.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [1. Clone & Virtual Environment](#1-clone--virtual-environment)
  - [2. Install Python Dependencies](#2-install-python-dependencies)
  - [3. Database Configuration](#3-database-configuration)
    - [Option A — SQLite (Simple Local)](#option-a--sqlite-simple-local)
    - [Option B — PostgreSQL (Recommended)](#option-b--postgresql-recommended)
  - [4. Run Database Migration](#4-run-database-migration)
  - [5. Start the Backend API](#5-start-the-backend-api)
  - [6. Start the Frontend](#6-start-the-frontend)
- [Environment Variables Reference](#environment-variables-reference)
- [Running Tests](#running-tests)
- [Production / Test Server Deployment](#production--test-server-deployment)
  - [1. Server Prerequisites](#1-server-prerequisites)
  - [2. Install & Configure PostgreSQL](#2-install--configure-postgresql)
  - [3. Install & Configure Nginx](#3-install--configure-nginx)
  - [4. Install & Configure Gunicorn via systemd](#4-install--configure-gunicorn-via-systemd)
  - [5. Deploy Using the Deploy Script](#5-deploy-using-the-deploy-script)

---

## Prerequisites

- **Python** 3.9 or higher
- **Node.js** 18+ and **npm**
- **PostgreSQL** 14+ (for non-SQLite environments)
- **Nginx** (for production/test server)
- **pip** and **venv**

---

## Local Development Setup

### 1. Clone & Virtual Environment

```bash
git clone <repository-url>
cd SprayPlanner

python3 -m venv sprayplan_env
source sprayplan_env/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install -r api/requirements.txt
pip install pytest   # Required for running tests
```

### 3. Database Configuration

The application supports **SQLite** (default, zero-config) or a **standalone PostgreSQL** server. Configuration is done entirely via environment variables — no code changes are needed to switch between them.

#### Option A — SQLite (Simple Local)

No extra steps required. The app defaults to SQLite automatically when `DB_TYPE` is not set.

#### Option B — PostgreSQL (Recommended)

**Step 1 — Install PostgreSQL locally** (macOS example using Homebrew):

```bash
brew install postgresql@15
brew services start postgresql@15
```

For Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

**Step 2 — Create the database and user:**

```bash
psql -U postgres
```

```sql
CREATE DATABASE sprayplanner;
CREATE USER sprayplanner_user WITH PASSWORD 'yourpassword';
grant sprayplanner_admins to sprayplanner_user;
GRANT CREATE ON SCHEMA public TO sprayplanner_admins;
\q
```

**Step 3 — Export environment variables:**

Set the following in your terminal session (or add them to a `.env` file or your shell profile):

```bash
export DB_TYPE=postgres
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=sprayplanner
export DB_USER=sprayplanner_user
export DB_PASSWORD=yourpassword
```

> **Tip:** You can also use a single `DATABASE_URL` connection string instead:
> ```bash
> export DATABASE_URL=postgresql://sprayplanner_user:yourpassword@localhost:5432/sprayplanner
> ```

### 4. Run Database Migration

Migrate and seed the PostgreSQL database from the CSV product file:

```bash
# Make sure environment variables are exported first (see Step 3 above)
PYTHONPATH=api python3 api/core/migrate_to_postgres.py
```

This will drop and recreate the `products` table and load all records from `spray_product_information.csv`.

### 5. Start the Backend API

```bash
source sprayplan_env/bin/activate
export PYTHONPATH=$(pwd)/api
python3 api/api.py
```

*The API will be available at `http://localhost:5001`.*

### 6. Start the Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm start
```

*The application will open in your browser at `http://localhost:3000`. Navigate to the **Database** link to manage chemical entries.*

---

## Environment Variables Reference

| Variable        | Required for Postgres | Default     | Description                                                       |
|-----------------|-----------------------|-------------|-------------------------------------------------------------------|
| `DB_TYPE`       | Yes                   | `sqlite`    | Set to `postgres` to use PostgreSQL, or omit/set `sqlite` for SQLite |
| `DB_HOST`       | Yes                   | `localhost` | Hostname or IP address of the PostgreSQL server                   |
| `DB_PORT`       | No                    | `5432`      | Port number of the PostgreSQL server                              |
| `DB_NAME`       | No                    | `sprayplanner` | Name of the PostgreSQL database                               |
| `DB_USER`       | No                    | `postgres`  | PostgreSQL login username                                         |
| `DB_PASSWORD`   | Yes                   | `postgres`  | PostgreSQL login password                                         |
| `DATABASE_URL`  | No                    | —           | Full PostgreSQL connection URL (overrides all individual `DB_*` vars) |
| `REACT_APP_API_URL` | No                | `http://localhost:5001/api/products` | API base URL used by the React frontend at build time |

---

## Running Tests

```bash
source sprayplan_env/bin/activate
PYTHONPATH=api pytest api/tests
```

---

## Production / Test Server Deployment

The deploy script `deploy.sh` handles building the frontend, transferring files to the server, running migrations, and restarting services. Before using it, you need to set up PostgreSQL, Nginx, and Gunicorn on the remote server.

### 1. Server Prerequisites

On your remote Ubuntu/Debian server:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgresql-contrib
```

### 2. Install & Configure PostgreSQL

On the **remote PostgreSQL server** (can be the same machine or a separate one):

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE sprayplanner;
CREATE USER sprayplanner_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE sprayplanner TO sprayplanner_user;
\q
```

If PostgreSQL is on a **separate server**, update `pg_hba.conf` to allow remote connections:

```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

Add the following line (replace with your app server's IP):

```
host    sprayplanner    sprayplanner_user    YOUR_APP_SERVER_IP/32    md5
```

Also update `postgresql.conf` to listen on all interfaces (or just the app server IP):

```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = '*'
```

Then restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 3. Install & Configure Nginx

**Step 1 — Copy the Nginx config template** to sites-available on your server:

```bash
sudo cp /var/www/sprayplanner/nginx.conf.template /etc/nginx/sites-available/sprayplanner
```

**Step 2 — Edit the config** and replace `YOUR_DOMAIN_OR_IP` with your server's domain or IP address:

```bash
sudo nano /etc/nginx/sites-available/sprayplanner
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    root /var/www/html/sprayplanner;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Step 3 — Enable the site and reload Nginx:**

```bash
sudo ln -sf /etc/nginx/sites-available/sprayplanner /etc/nginx/sites-enabled/sprayplanner
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Install & Configure Gunicorn via systemd

**Step 1 — Copy the systemd service template** to `/etc/systemd/system/`:

```bash
sudo cp /var/www/sprayplanner/sprayplanner-api.service.template \
        /etc/systemd/system/sprayplanner-api.service
```

**Step 2 — Edit the service file** and fill in your values:

```bash
sudo nano /etc/systemd/system/sprayplanner-api.service
```

Replace the placeholder values:

| Placeholder                         | Replace with                                      |
|-------------------------------------|---------------------------------------------------|
| `YOUR_SYSTEM_USER`                  | Your Linux user (e.g. `ubuntu`)                   |
| `YOUR_STANDALONE_POSTGRES_HOST`     | IP or hostname of your PostgreSQL server          |
| `YOUR_STANDALONE_POSTGRES_PASSWORD` | Your PostgreSQL password                          |

The complete service file should look like:

```ini
[Unit]
Description=Gunicorn instance to serve SprayPlanner Flask API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/sprayplanner/api
Environment="PATH=/var/www/sprayplanner/sprayplan_env/bin"
Environment="DB_TYPE=postgres"
Environment="DB_HOST=YOUR_DB_HOST"
Environment="DB_PORT=5432"
Environment="DB_NAME=sprayplanner"
Environment="DB_USER=sprayplanner_user"
Environment="DB_PASSWORD=yourpassword"
Environment="PYTHONPATH=/var/www/sprayplanner/api"
ExecStart=/var/www/sprayplanner/sprayplan_env/bin/gunicorn --workers 4 --bind 127.0.0.1:5001 api:app

[Install]
WantedBy=multi-user.target
```

**Step 3 — Enable and start the service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sprayplanner-api
sudo systemctl status sprayplanner-api
```

### 5. Deploy Using the Deploy Script

Once the server is configured, use `deploy.sh` from your local machine to build and deploy the app to `test` or `prod`:

```bash
chmod +x deploy.sh
./deploy.sh test ubuntu@YOUR_TEST_SERVER_IP
# or
./deploy.sh prod ubuntu@YOUR_PROD_SERVER_IP
```

The script will:
1. Run local unit tests.
2. Build the React frontend with the correct API URL.
3. Transfer backend Python files and the frontend build to the server.
4. Install/update Python dependencies in the remote virtual environment.
5. Run the PostgreSQL database migration to seed or update the database.
6. Copy static files to the Nginx web root.
7. Restart the `sprayplanner-api` systemd service.

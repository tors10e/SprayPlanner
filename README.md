# SprayPlanner

Application designed to determine what vineyard and orchard sprays to purchase based on growth stages, disease risks, and chemical constraints. It includes a Flask REST API backend, a React frontend for database management, and uses a containerized PostgreSQL database.

The entire application runs inside Docker for both local development and production deployments.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Running Tests](#running-tests)
- [Production Droplet / VPS Deployment](#production-droplet--vps-deployment)
  - [1. Provision Droplet](#1-provision-droplet)
  - [2. Deploying to the Server](#2-deploying-to-the-server)
  - [3. Domain and SSL Setup](#3-domain-and-ssl-setup)
- [Environment Variables Reference](#environment-variables-reference)

---

## Prerequisites

This application runs entirely inside Docker. You will need to install Docker on your local development machine:

### 1. Install Docker Desktop (macOS & Windows)
- **macOS**: Download and install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) (supports Apple Silicon and Intel).
- **Windows**: Download and install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/).
- *(Note: Docker Desktop includes both the Docker Engine and Docker Compose out of the box).*

### 2. Install Docker Engine & Compose (Linux / Ubuntu)
For standard Linux/Ubuntu machines, run the following commands to install Docker Engine and the Docker Compose plugin:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
# Add your user to the docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```
*(Please restart your terminal session after adding your user to the docker group to apply the changes).*

---

## Local Development Setup

To run the application locally:

### 1. Clone the repository
```bash
git clone <repository-url>
cd SprayPlanner
```

### 2. Create the configuration file
Copy the environment variables template to create your active `.env` file:
```bash
cp .env.example .env
```
*(By default, `.env` is configured with `APP_ENV=development` and maps database storage locally to `./pgdata_dev`)*

### 3. Spin up the containers
```bash
docker-compose up --build
```
This command builds and starts the multi-container stack:
- **PostgreSQL Database (`db`)** listening on port `5432` with files saved locally in `./pgdata_dev`.
- **Flask Backend (`backend`)** listening on port `5001`. It automatically waits for the database to start, runs migrations, and seeds lookup tables/campaign data on first boot.
- **Nginx Web Server (`frontend`)** served on `http://localhost`. It serves React assets and reverse-proxies `/api` calls.

### 4. Access the Application
Open your browser and navigate to:
- **Web App UI**: `http://localhost`
  - **Username**: `admin`
  - **Password**: `sprayplanner_admin`
- **Backend API Docs/Endpoints**: `http://localhost:5001/api/history`

---

## Running Tests

You can run the integration and unit test suite directly inside the running backend container without installing Python or dependencies on your host machine:

```bash
# Run tests inside the API container
docker exec -it sprayplanner-api pytest api/tests -v
```

---

## Production Droplet / VPS Deployment

This application is fully optimized for automated containerized deployment to any cloud provider virtual private server (VPS), such as a DigitalOcean Docker Droplet.

### 1. Provision Droplet
- If using **DigitalOcean**, select the **Docker One-Click App** from the Marketplace during droplet creation.
- If using a standard Linux instance, connect via SSH and install Docker:
  ```bash
  sudo apt update
  sudo apt install -y docker.io docker-compose
  sudo systemctl enable --now docker
  ```

### 2. Deploying to the Server
Connect to your droplet via SSH:

```bash
# Clone the repository
git clone <repository-url> /var/www/sprayplanner
cd /var/www/sprayplanner

# Copy configuration template
cp .env.example .env
```

Open `.env` in a text editor (e.g. `nano .env`) to customize settings for your production environment:
- Set **`APP_ENV=production`** (the Flask server will automatically resolve credentials from the `PROD_*` settings block).
- Set **`DB_VOLUME_PATH`** to map the database files directly to your attached block storage volume (e.g. `volume-nyc1-1783782660424`):
  ```ini
  DB_VOLUME_PATH=/mnt/volume-nyc1-1783782660424/postgres_data
  ```

Build and run the container stack in the background:
```bash
docker-compose up --build -d
```

### 3. Domain and SSL Setup
To map your domain and get free Let's Encrypt SSL certificates:

1. Map your domain DNS records (A record) to the droplet's IP address.
2. Connect to the droplet and run:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

---

## Environment Variables Reference

All configurations are managed inside the `.env` file. You can configure distinct connection settings for each environment using prefixes:

| Variable | Scope | Default | Description |
|---|---|---|---|
| `APP_ENV` | Global | `development` | The active environment: `production`, `test`, or `development` |
| `DB_VOLUME_PATH` | Global | `./pgdata` | Mount directory path for Postgres storage (e.g. custom attached droplet volume) |
| `DEV_DB_NAME` | Dev | `sprayplanner_dev` | Database name for development |
| `TEST_DB_NAME` | Test | `sprayplanner_test` | Database name for testing |
| `PROD_DB_NAME` | Prod | `sprayplanner` | Database name for production |
| `*_DB_HOST` | All | `db` | Database host container name inside Docker |
| `*_DB_USER` | All | `postgres` | Database login username |
| `*_DB_PASSWORD`| All | `Black1ce!` | Database login password |


## Build and deploy docker containers to container registry
docker buildx build --platform linux/amd64 \
  -t ghcr.io/tors10e/sprayplanner-frontend:latest \
  -f frontend/Dockerfile frontend \
  --push

docker buildx build --platform linux/amd64 \
  -t ghcr.io/tors10e/sprayplanner-api:latest \
  -f api/Dockerfile api \
  --push

docker buildx build --platform linux/amd64 \
  -t ghcr.io/tors10e/sprayplanner-api:latest \
  -f api/Dockerfile api \
  --push
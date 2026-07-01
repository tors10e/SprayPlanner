#!/bin/bash

# Native Deployment Script for SprayPlanner (No Docker)
set -e

# Configuration
APP_NAME="sprayplanner"
REMOTE_PATH="/var/www/sprayplanner"

echo "=========================================================="
echo "          SprayPlanner Native Deployment Script           "
echo "=========================================================="

# Check arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: ./deploy.sh [test|prod] [user@remote-ip]"
    echo ""
    echo "Example: ./deploy.sh test ubuntu@192.168.1.50"
    exit 1
fi

ENV_TARGET="$1"
REMOTE_SERVER="$2"

if [ "$ENV_TARGET" != "test" ] && [ "$ENV_TARGET" != "prod" ]; then
    echo "Error: Target environment must be 'test' or 'prod'."
    exit 1
fi

echo "Deploying to environment: $ENV_TARGET on server: $REMOTE_SERVER"

# Step 1: Run unit tests locally before deploying
echo "--> Step 1: Running unit tests locally..."
if [ -f "./sprayplan_env/bin/pytest" ]; then
    PYTHONPATH=api ./sprayplan_env/bin/pytest api/tests/
    echo "✓ Local tests passed!"
else
    echo "⚠️  Skipping tests (virtual environment or pytest not found)."
fi

# Step 2: Build the React frontend locally
echo "--> Step 2: Building frontend locally..."
read -p "Enter the public IP or Domain name of your remote server (for frontend API requests): " SERVER_HOST
REACT_APP_API_URL="http://${SERVER_HOST}/api/products"

cd frontend
echo "Installing frontend dependencies..."
npm install --legacy-peer-deps
echo "Building static React app with API URL: ${REACT_APP_API_URL}..."
REACT_APP_API_URL="${REACT_APP_API_URL}" npm run build
cd ..
echo "✓ Frontend built successfully!"

# Step 3: Bundle and copy application files to server
echo "--> Step 3: Creating remote directories and transferring files..."
# Make sure remote paths exist (you might need sudo on remote depending on permissions)
ssh "$REMOTE_SERVER" "sudo mkdir -p $REMOTE_PATH && sudo chown -R \$USER:\$USER $REMOTE_PATH"

# Copy API files and frontend built assets
scp api/requirements.txt "$REMOTE_SERVER:$REMOTE_PATH/requirements.txt"
scp -r api "$REMOTE_SERVER:$REMOTE_PATH/"
scp -r frontend/build "$REMOTE_SERVER:$REMOTE_PATH/"
scp nginx.conf.template "$REMOTE_SERVER:$REMOTE_PATH/"
scp sprayplanner-api.service.template "$REMOTE_SERVER:$REMOTE_PATH/"
echo "✓ File transfer complete!"

# Step 4: Standalone PostgreSQL connection settings for remote database migration
echo "--> Step 4: Configuring PostgreSQL standalone database connection on server..."
read -p "Enter Database Host (IP or hostname of remote PG server): " DB_HOST_INPUT
read -p "Enter Database Port [5432]: " DB_PORT_INPUT
DB_PORT_INPUT=${DB_PORT_INPUT:-5432}
read -p "Enter Database Name [sprayplanner]: " DB_NAME_INPUT
DB_NAME_INPUT=${DB_NAME_INPUT:-sprayplanner}
read -p "Enter Database User [postgres]: " DB_USER_INPUT
DB_USER_INPUT=${DB_USER_INPUT:-postgres}
read -s -p "Enter Database Password: " DB_PASS
echo ""

# Step 5: SSH and run remote setup commands (virtualenv setup, migrations, systemctl restart)
echo "--> Step 5: Setting up environment, running migrations, and restarting services..."

ssh "$REMOTE_SERVER" << EOF
  cd $REMOTE_PATH
  
  # Setup virtual environment if it doesn't exist
  if [ ! -d "sprayplan_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv sprayplan_env
  fi
  
  # Activate and install dependencies
  echo "Installing Python dependencies..."
  source sprayplan_env/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  
  # Export env variables and run database migration
  echo "Running database migration script..."
  export DB_TYPE="postgres"
  export DB_HOST="$DB_HOST_INPUT"
  export DB_PORT="$DB_PORT_INPUT"
  export DB_NAME="$DB_NAME_INPUT"
  export DB_USER="$DB_USER_INPUT"
  export DB_PASSWORD="$DB_PASS"
  
  PYTHONPATH=api python3 api/core/migrate_to_postgres.py
  
  # Copy static build to web server directory
  echo "Deploying frontend static files to Nginx web root..."
  sudo mkdir -p /var/www/html/sprayplanner
  sudo cp -r build/* /var/www/html/sprayplanner/
  sudo chown -R www-data:www-data /var/www/html/sprayplanner/
  
  # Restart systemd api service (assuming service is set up)
  echo "Restarting SprayPlanner API backend service..."
  if systemctl is-active --quiet sprayplanner-api; then
    sudo systemctl restart sprayplanner-api
  else
    echo "⚠️  sprayplanner-api systemd service is not yet enabled/active."
    echo "    Please copy $REMOTE_PATH/sprayplanner-api.service.template to /etc/systemd/system/sprayplanner-api.service,"
    echo "    configure it, and run: sudo systemctl daemon-reload && sudo systemctl enable --now sprayplanner-api"
  fi
EOF

echo "=========================================================="
echo "Deployment Finished!                                      "
echo "Please verify Gunicorn systemd service & Nginx are running."
echo "=========================================================="

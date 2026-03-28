# SprayPlanner
Application designed to determine what vineyard and orchard sprays to purchase based on growth stages, disease risks, and chemical constraints.

## Installation

### Prerequisites
- Python 3.9 or higher

### Procedures
1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd <project-root>
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv SprayPlanner/sprayplan_env
   source SprayPlanner/sprayplan_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r SprayPlanner/requirements.txt
   pip install pytest  # Required for running tests
   ```

## Usage

### Running the Application
To run the seasonal spray optimizer and view the generated plan:
```bash
source SprayPlanner/sprayplan_env/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python3 SprayPlanner/app.py
```

### Managing the Chemical Database (CRUD Frontend)
To manage the spray chemical database through the web interface, you must start both the backend API and the frontend application.

#### 1. Start the Backend API
In one terminal, activate the virtual environment and start the Flask server:
```bash
source SprayPlanner/sprayplan_env/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)/SprayPlanner/api
python3 SprayPlanner/api/api.py
```
*The API will run on `http://localhost:5001`.*

#### 2. Start the Frontend Application
In another terminal, navigate to the `frontend` directory and start the React app:
```bash
cd SprayPlanner/frontend
npm install
npm start
```
*The application will open in your browser. Navigate to the **Database** link in the menu to manage chemical entries.*

## Testing
To run the unit tests, ensure the virtual environment is activated and execute from the project root:
```bash
source SprayPlanner/sprayplan_env/bin/activate
export PYTHONPATH=$PYTHONPATH:.
pytest SprayPlanner/tests
```

import subprocess
import os
import sys

def main():
    # Get the directory of this script (SprayPlanner/)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the api directory (SprayPlanner/api)
    api_dir = os.path.join(base_dir, "api")
    
    # Add api_dir to PYTHONPATH so internal imports like 'core' work
    env = os.environ.copy()
    env["PYTHONPATH"] = api_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    # Path to python executable in venv
    venv_python = os.path.join(base_dir, "sprayplan_env/bin/python")
    
    if not os.path.exists(venv_python):
        # Fallback if venv is not exactly where expected
        venv_python = sys.executable
        print(f"Warning: Virtual environment not found at SprayPlanner/sprayplan_env. Using {venv_python}")

    # Path to api.py
    api_script = os.path.join(api_dir, "api.py")
    
    print(f"Starting Spray Chemical Database API on http://localhost:5001...")
    
    try:
        subprocess.run([venv_python, api_script], env=env)
    except KeyboardInterrupt:
        print("\nAPI stopped.")
    except Exception as e:
        print(f"Error starting API: {e}")

if __name__ == "__main__":
    main()

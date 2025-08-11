"""
Script to run command line scripts on Modal AI or locally.

USAGE:
    python run_script_on_modal.py <command_name> [--local]

ARGUMENTS:
    <command_name>  Required. Name of the command defined in commands.json
    --local         Optional. Run locally instead of on Modal AI cloud

EXAMPLES:
    # Run teleoperate command on Modal AI cloud
    python run_script_on_modal.py teleoperate
    
    # Run teleoperate command locally (for testing)
    python run_script_on_modal.py teleoperate --local
    
    # Show available commands
    python run_script_on_modal.py

COMMAND CONFIGURATION:
    Define your commands in commands.json in the same directory:
    {
        "command_name": {
            "command": "python -m module.name",
            "args": ["--arg1=value1", "--arg2=value2"]
        }
    }

REQUIREMENTS:
    - Modal AI account and authentication (for cloud execution)
    - commands.json file in the same directory
    - Required dependencies specified in the Modal image
"""

import json
import modal
import subprocess
from pathlib import Path

app = modal.App("lerobot-runner")

def load_commands(config_file="commands.json"):
    """Load commands from JSON config file."""
    config_path = Path(__file__).parent / config_file
    with open(config_path, 'r') as f:
        return json.load(f)

@app.function(
    image=modal.Image.debian_slim().pip_install([
        "lerobot",  # Add your lerobot dependencies here
        # Add other required packages
    ]).add_local_file("commands.json", remote_path="/root/commands.json"),
    timeout=3600,  # 1 hour timeout
)
def run_command_on_modal(command_name: str):
    """Run a command from the config file on Modal AI."""
    import subprocess
    import json
    
    # Load commands from mounted config file
    with open("/root/commands.json", 'r') as f:
        commands = json.load(f)
    
    if command_name not in commands:
        raise ValueError(f"Command '{command_name}' not found in config")
    
    cmd_config = commands[command_name]
    # Split the command properly
    command_parts = cmd_config["command"].split()
    full_command = command_parts + cmd_config["args"]
    
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
            "error": str(e)
        }

def run_local_command(command_name: str):
    """Run a command locally (for testing)."""
    commands = load_commands()
    
    if command_name not in commands:
        raise ValueError(f"Command '{command_name}' not found in config")
    
    cmd_config = commands[command_name]
    # Split the command properly
    command_parts = cmd_config["command"].split()
    full_command = command_parts + cmd_config["args"]
    
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
            "error": str(e)
        }

@app.function(
    image=modal.Image.debian_slim().pip_install([
        "fastapi[standard]",  # Required for web endpoints
    ])
)
@modal.fastapi_endpoint(method="POST")
def run_via_web(command_name: str):
    """Web endpoint to trigger command execution."""
    result = run_command_on_modal.remote(command_name)
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python run_script_on_modal.py <command_name> [--local]")
        print("Available commands:", list(load_commands().keys()))
        sys.exit(1)
    
    command_name = sys.argv[1]
    run_local = "--local" in sys.argv
    
    if run_local:
        print(f"Running '{command_name}' locally...")
        result = run_local_command(command_name)
    else:
        print(f"Running '{command_name}' on Modal AI...")
        with app.run():
            result = run_command_on_modal.remote(command_name)
    
    print("Result:", result)
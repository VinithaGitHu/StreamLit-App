import streamlit as st
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    try:
        import cx_Oracle
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cx_Oracle"])

def download_and_execute_script(repo_url, script_name, **kwargs):
    """Download the script from GitHub and execute it."""
    # Clone the repository
    repo_dir = "temp_repo"
    if not os.path.exists(repo_dir):
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)

    # Navigate to the repository folder and execute the script
    script_path = os.path.join(repo_dir, script_name)
    if not os.path.exists(script_path):
        st.error(f"Script {script_name} not found in the repository.")
        return

    # Execute the script
    command = [sys.executable, script_path]
    for key, value in kwargs.items():
        command.extend([f"--{key}", value])

    result = subprocess.run(command, text=True, capture_output=True)

    if result.returncode == 0:
        st.success("Script executed successfully.")
        st.text(result.stdout)
    else:
        st.error("Error executing the script.")
        st.text(result.stderr)

# Streamlit UI
st.title("Oracle Data Export to CSV")

# Input fields
repo_url = st.text_input("GitHub Repository URL", value="https://github.com/your-repo.git")
script_name = st.text_input("Script Name", value="fetch_and_export.py")
dsn = st.text_input("Oracle DSN")
user_id = st.text_input("Oracle User ID")
password = st.text_input("Oracle Password", type="password")
output_path = st.text_input("Output Directory", value="C:\\Temp\\Streamlit-CSV")

# Execute button
if st.button("Execute Script"):
    if not all([repo_url, script_name, dsn, user_id, password, output_path]):
        st.error("Please fill in all fields.")
    else:
        install_dependencies()
        download_and_execute_script(
            repo_url,
            script_name,
            dsn=dsn,
            user=user_id,
            password=password,
            output_path=output_path,
        )

import os
import sys
import subprocess
import webbrowser
import time

def main():
    # Detect if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_path, "app.py")
    
    # Ensure app.py exists
    if not os.path.exists(app_path):
        print(f"Error: Could not locate app.py at {app_path}")
        sys.exit(1)
        
    print("==================================================")
    print("      Smart Job Recommendation Agent Launcher     ")
    print("==================================================")
    print("Booting local Streamlit server...")
    
    # Launch Streamlit server as subprocess
    # sys.executable points to the bundled python interpreter when frozen
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false"
    ]
    
    # Start process
    proc = subprocess.Popen(cmd)
    
    # Wait for server to bind port, then open user browser
    time.sleep(2.5)
    print("Opening web interface at http://localhost:8501 ...")
    webbrowser.open("http://localhost:8501")
    print("\nPress Ctrl+C inside this window to terminate the application.")
    
    try:
        while True:
            # Check if subprocess died
            if proc.poll() is not None:
                print("Streamlit process terminated unexpectedly.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTerminating server. Goodbye!")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()

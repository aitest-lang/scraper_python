#!/usr/bin/env python3
"""
Recon Tool Launcher
Launches the Streamlit web interface for reconnaissance
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit reconnaissance tool"""
    print("🚀 Launching Recon Tool...")
    print("🔍 Professional Contact Reconnaissance Tool")
    print("📧 Extract contact information from professional profiles")
    print()

    try:
        # Launch Streamlit app
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'],
                     cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n👋 Recon Tool stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()

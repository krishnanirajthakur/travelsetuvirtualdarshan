"""
Photo Compositor - Streamlit Application
Main entry point for Streamlit Cloud deployment
"""
import subprocess
import sys

# Run the photocompositor module
if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "photocompositor.py"])

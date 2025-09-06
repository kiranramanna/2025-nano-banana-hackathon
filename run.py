#!/usr/bin/env python3
"""
Main runner script for the AI Storybook Generator
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'google.genai',
        'PIL',
        'dotenv',
        'reportlab',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False
    return True

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting backend server on port 5000...")
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)
    subprocess.Popen([sys.executable, "app.py"])
    os.chdir("..")
    time.sleep(3)

def open_frontend():
    """Open the frontend in the default browser"""
    print("🌐 Opening frontend in browser...")
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    webbrowser.open(f"file://{frontend_path.absolute()}")

def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║     🎨 AI Storybook Generator 📚         ║
    ║        Powered by Gemini 2.5 Flash       ║
    ╚══════════════════════════════════════════╝
    """)
    
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating from template...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 Please update .env with your API keys")
            return
    
    print("📦 Checking dependencies...")
    if not check_dependencies():
        print("🔄 Dependencies installed. Please run the script again.")
        return
    
    print("✅ All dependencies satisfied")
    
    try:
        start_backend()
        open_frontend()
        
        print("\n✨ AI Storybook Generator is running!")
        print("Backend: http://localhost:5000")
        print("Frontend: Open in your browser")
        print("\nPress Ctrl+C to stop the server\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Storybook Generator...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
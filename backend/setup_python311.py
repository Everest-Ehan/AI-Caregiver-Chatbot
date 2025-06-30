#!/usr/bin/env python3
"""
Setup script for Python 3.11 compatibility
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 11:
        print("❌ Error: Python 3.11 or higher is required")
        print("Please install Python 3.11 and try again")
        return False
    
    if version.minor >= 13:
        print("⚠️  Warning: Python 3.13+ may have dependency conflicts")
        print("Consider using Python 3.11 or 3.12 for better compatibility")
    
    print("✅ Python version is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    print("\n🔧 Creating .env file...")
    
    env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Model Configuration
MODEL_NAME=gpt-4o
MODEL_TEMPERATURE=0.4
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update OPENAI_API_KEY with your actual API key")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_imports():
    """Test if all imports work correctly"""
    print("\n🧪 Testing imports...")
    
    try:
        # Test basic imports
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn imported successfully")
        
        # Test LangChain imports
        import langchain
        import langchain_openai
        import langchain_community
        print("✅ LangChain packages imported successfully")
        
        # Test LangGraph imports
        import langgraph
        print("✅ LangGraph imported successfully")
        
        # Test our agent
        from agents.caregiver_agent import create_caregiver_agent
        print("✅ Caregiver agent imported successfully")
        
        print("✅ All imports working correctly")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up AI Caregiver Chatbot for Python 3.11")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update the OPENAI_API_KEY in .env file")
    print("2. Run: python run.py")
    print("3. Open http://localhost:8000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
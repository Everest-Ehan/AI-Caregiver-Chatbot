#!/usr/bin/env python3
"""
Test script for Python 3.11 compatibility
"""

import sys
import os

def test_python_version():
    """Test Python version compatibility"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ detected - compatible")
        return True
    else:
        print("❌ Python 3.11+ required")
        return False

def test_imports():
    """Test critical imports"""
    print("\nTesting imports...")
    
    try:
        # Test basic imports
        import fastapi
        print("✅ FastAPI imported")
        
        import uvicorn
        print("✅ Uvicorn imported")
        
        # Test LangChain imports
        import langchain
        print("✅ LangChain imported")
        
        import langchain_openai
        print("✅ LangChain OpenAI imported")
        
        import langgraph
        print("✅ LangGraph imported")
        
        # Test our modules
        from agents.caregiver_agent import create_caregiver_agent
        print("✅ Caregiver agent imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_creation():
    """Test agent creation"""
    print("\nTesting agent creation...")
    
    try:
        from agents.caregiver_agent import create_caregiver_agent
        
        # Create agent
        agent = create_caregiver_agent()
        print("✅ Agent created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from agents.caregiver_agent import create_caregiver_agent
        from langchain.schema import HumanMessage
        
        # Create agent
        agent = create_caregiver_agent()
        
        # Test with a simple message
        result = agent.invoke({
            "messages": [HumanMessage(content="Hi, I need help with clocking in")],
            "scenario_id": "clock_in_issue"
        })
        
        print("✅ Basic functionality test passed")
        print(f"Response received: {len(result.get('messages', []))} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Python 3.11 Compatibility")
    print("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("Imports", test_imports),
        ("Agent Creation", test_agent_creation),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*40}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Python 3.11 setup is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
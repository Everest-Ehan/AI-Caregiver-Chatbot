#!/usr/bin/env python3
"""
Simple test script to debug LangGraph agent issues
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agent_creation():
    """Test if the agent can be created"""
    try:
        from agents.caregiver_agent import create_caregiver_agent
        print("✅ Successfully imported create_caregiver_agent")
        
        agent = create_caregiver_agent()
        if agent is None:
            print("❌ Agent creation returned None")
            return False
        else:
            print("✅ Agent created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_invocation():
    """Test if the agent can be invoked"""
    try:
        from agents.caregiver_agent import create_caregiver_agent
        from langchain.schema import HumanMessage
        
        agent = create_caregiver_agent()
        if agent is None:
            print("❌ Cannot test invocation - agent is None")
            return False
        
        # Test state
        test_state = {
            "messages": [HumanMessage(content="Hi, I'm having trouble clocking in")],
            "session_id": "test_session",
            "scenario_id": "clock_in_issue",
            "context_data": {"client_name": "John Smith"}
        }
        
        print(f"Testing with state: {test_state}")
        result = agent.invoke(test_state)
        print(f"Result: {result}")
        
        if result is None:
            print("❌ Agent invocation returned None")
            return False
        else:
            print("✅ Agent invocation successful")
            return True
            
    except Exception as e:
        print(f"❌ Error invoking agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing LangGraph Agent...")
    print("=" * 50)
    
    # Test 1: Agent creation
    print("\n1. Testing agent creation...")
    creation_success = test_agent_creation()
    
    # Test 2: Agent invocation
    if creation_success:
        print("\n2. Testing agent invocation...")
        invocation_success = test_agent_invocation()
    else:
        print("\n2. Skipping invocation test due to creation failure")
        invocation_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Agent Creation: {'✅ PASS' if creation_success else '❌ FAIL'}")
    print(f"Agent Invocation: {'✅ PASS' if invocation_success else '❌ FAIL'}")
    
    if not creation_success or not invocation_success:
        print("\n❌ Agent tests failed. Check the error messages above.")
        exit(1)
    else:
        print("\n✅ All agent tests passed!") 
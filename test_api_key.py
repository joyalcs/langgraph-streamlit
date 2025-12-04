"""
Quick test to verify OpenAI API key is configured correctly
"""
import os

print("=" * 60)
print("OpenAI API Key Configuration Test")
print("=" * 60)

# Check if API key is set
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("\n❌ OPENAI_API_KEY is NOT set!")
    print("\nYou need to set your OpenAI API key.")
    print("\nOption 1 - Set in current session (temporary):")
    print('  $env:OPENAI_API_KEY = "sk-your-api-key-here"')
    print("\nOption 2 - Set permanently (Windows):")
    print("  1. Press Win + R")
    print("  2. Type: sysdm.cpl")
    print("  3. Advanced tab → Environment Variables")
    print("  4. Add User variable: OPENAI_API_KEY = sk-...")
    print("\nOption 3 - Use Groq instead (free):")
    print("  1. Get key from: https://console.groq.com/")
    print("  2. Update base_agent.py to use ChatGroq")
else:
    print(f"\n✅ OPENAI_API_KEY is set")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:7]}...")
    
    # Test if it actually works
    print("\n📡 Testing API key with OpenAI...")
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        response = llm.invoke("Say 'API key works!'")
        
        print(f"✅ SUCCESS! API key is valid")
        print(f"   Response: {response.content}")
        
    except Exception as e:
        print(f"\n❌ API key is set but not working!")
        print(f"   Error: {e}")
        print("\nPossible issues:")
        print("  - API key is invalid")
        print("  - API key doesn't have credits")
        print("  - Network/firewall blocking OpenAI")

print("\n" + "=" * 60)

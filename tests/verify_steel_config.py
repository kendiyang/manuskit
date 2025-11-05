#!/usr/bin/env python3
"""
Quick verification script to check Steel configuration.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_steel_config():
    """Verify Steel configuration and display mode"""
    
    print("=" * 60)
    print("Steel Configuration Verification")
    print("=" * 60)
    
    steel_api_key = os.getenv("STEEL_API_KEY", "")
    steel_base_url = os.getenv("STEEL_BASE_URL", "")
    
    print(f"\n📋 Current Configuration:")
    print(f"   STEEL_API_KEY: {'✅ Set (' + steel_api_key[:10] + '...)' if steel_api_key and steel_api_key.strip() else '❌ Empty'}")
    print(f"   STEEL_BASE_URL: {'✅ ' + steel_base_url if steel_base_url else '❌ Empty'}")
    
    print(f"\n🔍 Detected Mode:")
    
    has_api_key = bool(steel_api_key and steel_api_key.strip())
    has_base_url = bool(steel_base_url)
    
    if has_api_key and has_base_url:
        print("   🌐 HYBRID MODE")
        print("   → Official Steel with custom endpoint")
        print(f"   → API Key: {steel_api_key[:15]}...")
        print(f"   → Base URL: {steel_base_url}")
    elif has_api_key:
        print("   ☁️  OFFICIAL STEEL MODE")
        print("   → Using Steel's hosted service")
        print(f"   → API Key: {steel_api_key[:15]}...")
    elif has_base_url:
        print("   🏠 SELF-HOSTED STEEL MODE")
        print("   → Using your own Steel infrastructure")
        print(f"   → Base URL: {steel_base_url}")
    else:
        print("   💻 LOCAL BROWSER MODE (Fallback)")
        print("   → No Steel configuration found")
        print("   → Will use local Playwright browser")
    
    print(f"\n📊 Other Configuration:")
    print(f"   MODEL: {os.getenv('MODEL', 'not set')}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"   OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'default')}")
    
    print("\n" + "=" * 60)
    
    # Check if self-hosted Steel is reachable
    if has_base_url and not has_api_key:
        print("\n🔌 Testing self-hosted Steel connectivity...")
        try:
            import requests
            response = requests.get(f"{steel_base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Self-hosted Steel is reachable")
            else:
                print(f"   ⚠️  Steel responded with status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot connect to {steel_base_url}")
            print(f"   → Check if Steel service is running")
        except requests.exceptions.Timeout:
            print(f"   ⚠️  Connection timeout to {steel_base_url}")
        except Exception as e:
            print(f"   ⚠️  Could not test connectivity: {e}")
    
    print("\n💡 Next Steps:")
    if not has_api_key and not has_base_url:
        print("   1. Add STEEL_API_KEY or STEEL_BASE_URL to .env")
        print("   2. Restart the server")
    else:
        print("   1. Start server: python src/main.py")
        print("   2. Test extraction: python test_extraction.py")
        print("   3. Check logs for Steel connection status")
    
    print("=" * 60 + "\n")

if __name__ == "__main__":
    verify_steel_config()

#!/usr/bin/env python3
"""
Test CDP URL construction for different Steel modes
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_cdp_url_logic():
    """Test CDP URL construction logic for official and self-hosted Steel"""
    
    print("=" * 70)
    print("Steel CDP URL Construction Test")
    print("=" * 70)
    
    # Test scenarios
    scenarios = [
        {
            "name": "Official Steel",
            "steel_api_key": "sk_live_test123456789",
            "steel_base_url": None,
            "session_id": "abc123-def456-ghi789",
            "session_websocket_url": None,
        },
        {
            "name": "Self-hosted Steel (with websocket_url)",
            "steel_api_key": None,
            "steel_base_url": "http://10.92.40.135:3000",
            "session_id": "xyz789-uvw456-rst123",
            "session_websocket_url": "ws://10.92.40.135:3000/",
        },
        {
            "name": "Self-hosted Steel (without websocket_url)",
            "steel_api_key": None,
            "steel_base_url": "http://10.92.40.135:3000",
            "session_id": "lmn456-opq789-rst012",
            "session_websocket_url": None,
        },
        {
            "name": "Hybrid Mode (API key + base URL)",
            "steel_api_key": "sk_live_test123456789",
            "steel_base_url": "https://custom.steel.endpoint",
            "session_id": "hybrid123-test456",
            "session_websocket_url": "wss://custom.steel.endpoint/",
        },
    ]
    
    for scenario in scenarios:
        print(f"\n{'─' * 70}")
        print(f"Scenario: {scenario['name']}")
        print(f"{'─' * 70}")
        print(f"  steel_api_key: {scenario['steel_api_key'][:20] + '...' if scenario['steel_api_key'] else 'None'}")
        print(f"  steel_base_url: {scenario['steel_base_url']}")
        print(f"  session.id: {scenario['session_id']}")
        print(f"  session.websocket_url: {scenario['session_websocket_url']}")
        
        # Simulate the logic from extraction_service.py
        steel_api_key = scenario['steel_api_key']
        steel_base_url = scenario['steel_base_url']
        session_id = scenario['session_id']
        websocket_url = scenario['session_websocket_url']
        
        cdp_url = None
        method = None
        
        # Official Steel check (has API key, no base URL)
        if steel_api_key and steel_api_key.strip() and not steel_base_url:
            cdp_url = f"wss://connect.steel.dev?apiKey={steel_api_key}&sessionId={session_id}"
            method = "Official Steel (constructed)"
        
        # Self-hosted: Prioritize base_url
        elif steel_base_url:
            # Replace protocol
            if steel_base_url.startswith('http://'):
                cdp_url = steel_base_url.replace('http://', 'ws://')
            elif steel_base_url.startswith('https://'):
                cdp_url = steel_base_url.replace('https://', 'wss://')
            else:
                cdp_url = steel_base_url
            method = "Constructed from base_url (prioritized)"
        
        # Fallback: use websocket_url from session
        elif websocket_url:
            cdp_url = websocket_url
            method = "Session websocket_url (fallback)"
        
        else:
            cdp_url = "ERROR: Unable to determine CDP URL"
            method = "Error"
        
        print(f"\n  ✅ Method: {method}")
        print(f"  🔗 CDP URL: {cdp_url}")
    
    print(f"\n{'=' * 70}")
    print("\nCurrent Environment Configuration:")
    print(f"{'=' * 70}")
    
    current_api_key = os.getenv("STEEL_API_KEY", "")
    current_base_url = os.getenv("STEEL_BASE_URL", "")
    
    print(f"  STEEL_API_KEY: {current_api_key[:20] + '...' if current_api_key and current_api_key.strip() else 'Empty'}")
    print(f"  STEEL_BASE_URL: {current_base_url if current_base_url else 'Empty'}")
    
    # Determine current mode
    if current_api_key and current_api_key.strip() and not current_base_url:
        print(f"\n  Current Mode: ☁️  Official Steel")
        print(f"  Expected CDP: wss://connect.steel.dev?apiKey=...&sessionId=...")
    elif current_api_key and current_api_key.strip() and current_base_url:
        print(f"\n  Current Mode: 🌐 Hybrid (API key + custom endpoint)")
        print(f"  Expected CDP: session.websocket_url or constructed from base_url")
    elif current_base_url:
        print(f"\n  Current Mode: 🏠 Self-hosted Steel")
        print(f"  Expected CDP: {current_base_url.replace('http://', 'ws://').replace('https://', 'wss://')}")
    else:
        print(f"\n  Current Mode: 💻 Local Browser (no Steel)")
    
    print(f"\n{'=' * 70}\n")

if __name__ == "__main__":
    test_cdp_url_logic()

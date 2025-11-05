"""
Enhanced Steel Browser Use Test Script
Demonstrates best practices for Steel + browser-use integration.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from steel import Steel
from browser_use import Agent, BrowserSession
from browser_use.llm.openai.chat import ChatOpenAI

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.ENDC}\n")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def validate_config():
    """Validate required configuration"""
    print_header("Configuration Validation")
    
    required_vars = {
        "STEEL_BASE_URL": os.getenv("STEEL_BASE_URL"),
        "MODEL": os.getenv("MODEL"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
    }
    
    print_info(f"Loaded .env from: {env_path}")
    print("\nConfiguration:")
    
    all_valid = True
    for key, value in required_vars.items():
        if key == "OPENAI_API_KEY":
            display_value = f"{value[:10]}...{value[-4:]}" if value else None
        else:
            display_value = value
        
        if value:
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {key}: {display_value}")
        else:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} {key}: Not set")
            all_valid = False
    
    # Critical checks
    if not required_vars["OPENAI_API_KEY"]:
        print_error("OPENAI_API_KEY is required!")
        sys.exit(1)
    
    if not required_vars["STEEL_BASE_URL"]:
        print_warning("STEEL_BASE_URL not set - will use local browser")
    
    if all_valid:
        print_success("All configurations valid")
    
    return required_vars


def replace_protocol_mapping(url):
    """Convert HTTP/HTTPS to WebSocket protocol"""
    if not url:
        return None
    
    protocol_mapping = {
        'http://': 'ws://',
        'https://': 'wss://'
    }
    
    for old_protocol, new_protocol in protocol_mapping.items():
        if url.startswith(old_protocol):
            return url.replace(old_protocol, new_protocol)
    return url


async def run_browser_automation(task: str):
    """
    Run browser automation task with Steel + browser-use.
    
    Args:
        task: Natural language task description
    """
    steel_client = None
    session = None
    
    try:
        print_header("Initializing Browser Automation")
        
        # Initialize Steel client
        steel_base_url = os.getenv("STEEL_BASE_URL")
        use_steel = bool(steel_base_url)
        
        if use_steel:
            print_info(f"Using Steel at: {steel_base_url}")
            steel_client = Steel(base_url=steel_base_url)
            
            # Create Steel session
            print_info("Creating Steel session...")
            session = steel_client.sessions.create()
            print_success(f"Session created: {session.session_viewer_url}")
            
            # Prepare CDP URL
            cdp_url = replace_protocol_mapping(steel_base_url)
            print_info(f"CDP URL: {cdp_url}")
            
            # Create browser session
            browser_session = BrowserSession(cdp_url=cdp_url)
        else:
            print_warning("Using local browser (Steel not configured)")
            browser_session = BrowserSession()
        
        # Create LLM model
        print_info(f"Creating LLM with model: {os.getenv('MODEL')}")
        model = ChatOpenAI(
            model=os.getenv("MODEL"),
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        
        # Create AI agent
        print_info("Creating AI agent...")
        agent = Agent(
            task=task,
            llm=model,
            browser_session=browser_session
        )
        
        # Run the agent
        print_header("Running Agent")
        print_info(f"Task: {task}")
        print()
        
        start_time = time.time()
        result = await agent.run()
        elapsed_time = time.time() - start_time
        
        print()
        print_success(f"Task completed in {elapsed_time:.2f} seconds!")
        
        # Display result if available
        if result:
            print(f"\n{Colors.OKCYAN}Result:{Colors.ENDC}")
            print(f"{result}")
        
        return result
        
    except KeyboardInterrupt:
        print_warning("\nTask interrupted by user")
        return None
        
    except Exception as e:
        print_error(f"Task failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # Clean up resources
        if steel_client and session:
            try:
                print_info("Releasing Steel session...")
                steel_client.sessions.release(session.id)
                print_success("Session released")
            except Exception as e:
                print_warning(f"Failed to release session: {e}")


async def main():
    """Main execution function"""
    print_header("Steel + browser-use Integration Test")
    
    # Validate configuration
    config = validate_config()
    
    # Define test task
    task = "Go to docs.steel.dev, open the changelog, and tell me what's new."
    
    # Run browser automation
    result = await run_browser_automation(task)
    
    # Final status
    print_header("Test Complete")
    if result:
        print_success("Test passed!")
    else:
        print_warning("Test completed with warnings or errors")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n\nScript interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nFatal error: {e}")
        sys.exit(1)

"""
Steel Browser Use Starter Template
Integrates Steel with browser-use framework to create an AI agent for web interactions.
Requires STEEL_API_KEY & OPENAI_API_KEY in .env file.
"""
 
import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from steel import Steel
from browser_use import Agent, BrowserSession
from browser_use.llm.openai.chat import ChatOpenAI  # Use browser-use's ChatOpenAI, not langchain's

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
print(f"\n{'='*60}")
print(f"Loaded .env from: {env_path}")
print(f"{'='*60}\n")

# Validate required configuration
required_vars = {
    "STEEL_BASE_URL": os.getenv("STEEL_BASE_URL"),
    "MODEL": os.getenv("MODEL"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
}

print("Configuration:")
for key, value in required_vars.items():
    if key == "OPENAI_API_KEY":
        # Mask API key
        display_value = f"{value[:10]}...{value[-4:]}" if value else "Not set"
    else:
        display_value = value or "Not set"
    print(f"  {key}: {display_value}")

# Check for missing critical configs
if not required_vars["OPENAI_API_KEY"]:
    raise ValueError("OPENAI_API_KEY is required in .env file")

if not required_vars["MODEL"]:
    raise ValueError("MODEL is required in .env file")

if not required_vars["STEEL_BASE_URL"]:
    print("\n⚠️  Warning: STEEL_BASE_URL not set, will use local browser\n")

print(f"{'='*60}\n")

def replace_protocol_mapping(url):
    protocol_mapping = {
        'http://': 'ws://',
        'https://': 'wss://'
    }
    
    for old_protocol, new_protocol in protocol_mapping.items():
        if url.startswith(old_protocol):
            return url.replace(old_protocol, new_protocol)
    return url

 
# Initialize the Steel client with API key
client = Steel(base_url=os.getenv("STEEL_BASE_URL"))
 
# Create a Steel session
print("Creating Steel session...")
session = client.sessions.create()
print(f"Session created at {session.session_viewer_url}")
 
# Connect browser-use to Steel via CDP
# Use STEEL_BASE_URL instead of DOMAIN for consistency
cdp_url = replace_protocol_mapping(os.getenv("STEEL_BASE_URL") or os.getenv("DOMAIN", "http://localhost:3000"))
 
# Create and configure the AI agent
model_name = os.getenv("MODEL")
if not model_name:
    raise ValueError("MODEL environment variable is required")

print(f"Creating LLM with model: {model_name}")
model = ChatOpenAI(
    model=model_name,
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    # DeepSeek doesn't support response_format with JSON schema
    # Use add_schema_to_system_prompt instead
    add_schema_to_system_prompt=True,
)
print(f"LLM created successfully (DeepSeek-compatible mode)")
 
task = "Go to docs.steel.dev, open the changelog, and tell me what's new."
 
# Create agent with DeepSeek-compatible settings
# DeepSeek doesn't support structured response_format, so disable it
agent = Agent(
    task=task,
    llm=model,
    browser_session=BrowserSession(cdp_url=cdp_url),
    use_vision=False,  # DeepSeek doesn't support vision
)
 
async def main():
  try:
      # Run the agent
      print("Running the agent...")
      await agent.run()
      print("Task completed!")
      
  except Exception as e:
      print(f"An error occurred: {e}")
  finally:
      time.sleep(10)
      
      # Clean up resources
      if session:
          client.sessions.release(session.id)
          print("Session released")
      print("Done!")
 
# Run the async main function
if __name__ == '__main__':
    asyncio.run(main())
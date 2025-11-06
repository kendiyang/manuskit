"""
Web content extraction service using Steel SDK and browser-use.
Implements intelligent content extraction from web pages.
"""
import asyncio
import logging
import os
import json
import re
from typing import Optional, Dict, Any, List
from steel import Steel
from browser_use import Agent, BrowserSession
from browser_use.llm.openai.chat import ChatOpenAI

from src.models import ExtractionResult, ContentSection, PostMetadata

logger = logging.getLogger(__name__)


def replace_protocol_mapping(url: str) -> str:
    """Convert HTTP/HTTPS protocol to WebSocket protocol"""
    protocol_mapping = {
        'http://': 'ws://',
        'https://': 'wss://'
    }
    
    for old_protocol, new_protocol in protocol_mapping.items():
        if url.startswith(old_protocol):
            return url.replace(old_protocol, new_protocol)
    return url


class ExtractionService:
    """Service for extracting structured content from websites"""
    
    def __init__(
        self,
        steel_api_key: Optional[str] = None,
        steel_base_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize extraction service
        
        Args:
            steel_api_key: Steel API key (defaults to STEEL_API_KEY env var)
            steel_base_url: Optional custom Steel endpoint
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            openai_base_url: Optional custom OpenAI endpoint
            model: LLM model to use for extraction
        """
        self.steel_api_key = steel_api_key or os.getenv("STEEL_API_KEY", "")
        self.steel_base_url = steel_base_url or os.getenv("STEEL_BASE_URL")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_BASE_URL")
        # Fix: use MODEL instead of MODEL_NAME
        self.model = model or os.getenv("MODEL", "gpt-4o-mini")
        
        # Log configuration (mask sensitive data)
        logger.info(f"Initializing ExtractionService with model: {self.model}")
        logger.info(f"Steel Base URL: {self.steel_base_url}")
        logger.info(f"OpenAI Base URL: {self.openai_base_url}")
        logger.info(f"Steel API Key configured: {bool(self.steel_api_key and self.steel_api_key.strip())}")
        logger.info(f"OpenAI API Key configured: {bool(self.openai_api_key)}")
        
        # Validate Steel configuration
        if self.steel_api_key and self.steel_api_key.strip():
            logger.info("Steel API Key configured - will use official Steel service")
        elif self.steel_base_url:
            logger.info("Steel Base URL configured - will use self-hosted Steel service")
        else:
            logger.warning("Neither STEEL_API_KEY nor STEEL_BASE_URL configured - will use local browser")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.model:
            raise ValueError("MODEL is required")
    
    def _create_steel_client(self) -> Steel:
        """
        Create Steel client instance.
        
        Supports two modes:
        1. Official Steel: Use STEEL_API_KEY (base_url is optional)
        2. Self-hosted Steel: Use STEEL_BASE_URL (api_key not required)
        """
        steel_params = {}
        
        # Official Steel with API key
        if self.steel_api_key and self.steel_api_key.strip():
            steel_params["steel_api_key"] = self.steel_api_key
            logger.info("Creating Steel client with API key (official Steel)")
        
        # Self-hosted Steel with base URL
        if self.steel_base_url:
            steel_params["base_url"] = self.steel_base_url
            logger.info(f"Creating Steel client with base_url: {self.steel_base_url} (self-hosted Steel)")
        
        return Steel(**steel_params)
    
    def _create_llm(self) -> ChatOpenAI:
        """Create LLM instance for AI agent"""
        logger.info(f"Creating LLM with model: {self.model}")
        
        # browser-use's ChatOpenAI parameters
        llm_params = {
            "model": self.model,
            "temperature": 0.3,
            "api_key": self.openai_api_key,
        }
        
        # Add base_url if provided (for custom endpoints)
        if self.openai_base_url:
            llm_params["base_url"] = self.openai_base_url
        
        # Check if model is DeepSeek (which doesn't support response_format)
        is_deepseek = "deepseek" in self.model.lower()
        if is_deepseek:
            logger.warning(f"DeepSeek model detected: {self.model}")
            logger.warning("DeepSeek does NOT support structured output (response_format)")
            logger.warning("This will cause failures. Please use gpt-4o, gpt-4o-mini, or claude instead.")
            # Note: add_schema_to_system_prompt doesn't help because browser-use 
            # still tries to use response_format at the API level
        
        llm = ChatOpenAI(**llm_params)
        logger.info(f"LLM created: provider={llm.provider}, model={llm.model}")
        return llm
    
    async def extract_reddit_answers(self, question: str) -> ExtractionResult:
        """
        Extract structured content from Reddit Answers for a given question.
        
        Args:
            question: Question to search for on Reddit Answers
            
        Returns:
            ExtractionResult with structured data
        """
        steel_client = None
        session = None
        
        try:
            logger.info(f"Starting extraction for question: {question}")
            
            # Decide whether to use Steel (if API key OR base URL provided)
            use_steel = bool(
                (self.steel_api_key and self.steel_api_key.strip()) or 
                self.steel_base_url
            )
            browser_session = None
            
            if use_steel:
                # Create Steel session
                if self.steel_api_key and self.steel_api_key.strip():
                    logger.info("Using official Steel SDK for browser automation")
                else:
                    logger.info("Using self-hosted Steel SDK for browser automation")
                
                steel_client = self._create_steel_client()
                session = steel_client.sessions.create()
                logger.info(f"Steel session created: {session.session_viewer_url}")
                
                # Get CDP URL for browser-use connection
                # Official Steel: Use wss://connect.steel.dev with apiKey and sessionId
                # Self-hosted Steel: Use websocket_url from session or construct from base_url
                
                if self.steel_api_key and self.steel_api_key.strip() and not self.steel_base_url:
                    # Official Steel: construct official CDP URL
                    cdp_url = f"wss://connect.steel.dev?apiKey={self.steel_api_key}&sessionId={session.id}"
                    logger.info(f"Using official Steel CDP URL: wss://connect.steel.dev?sessionId={session.id[:8]}...")
                
                elif self.steel_base_url:
                    # Self-hosted Steel: prioritize base_url to construct CDP URL
                    cdp_url = replace_protocol_mapping(self.steel_base_url)
                    logger.info(f"Using self-hosted Steel CDP URL from base_url: {cdp_url}")
                
                elif hasattr(session, 'websocket_url') and session.websocket_url:
                    # Fallback: use session.websocket_url if base_url not available
                    cdp_url = session.websocket_url
                    logger.info(f"Using Steel session websocket_url (fallback): {cdp_url}")
                
                else:
                    raise ValueError("Unable to determine CDP URL for Steel session")
                
                browser_session = BrowserSession(cdp_url=cdp_url)
            else:
                logger.info("STEEL not configured — running with local browser session")
                browser_session = BrowserSession()
            
            # Create AI agent with extraction task
            logger.info("Creating LLM and AI agent...")
            llm = self._create_llm()
            
            # Detailed extraction prompt for Reddit Answers
            task = f"""
            Go to https://www.reddit.com/answers/ and search for: "{question}"
            
            Then extract and structure the following information:
            1. The full URL of the Reddit Answers page
            2. The exact question as displayed
            3. All source subreddit URLs mentioned
            4. All answer sections with their headings and content (as separate paragraphs)
            5. Related posts with rank, title, subreddit, URL, upvotes, comments, domain, promoted status, and score
            6. Related topics/questions suggested
            
            Return the data in JSON format following this structure:
            {{
                "url": "full URL",
                "question": "the question",
                "sources": ["list", "of", "subreddit", "urls"],
                "sections": [
                    {{"heading": "Section Name", "content": ["paragraph 1", "paragraph 2"]}}
                ],
                "relatedPosts": [
                    {{
                        "rank": "1",
                        "title": "Post title",
                        "subreddit": "subreddit_name",
                        "url": "post url",
                        "upvotes": 123,
                        "comments": 45,
                        "domain": "domain",
                        "promoted": false,
                        "score": 123
                    }}
                ],
                "relatedTopics": ["related question 1", "related question 2"]
            }}
            """
            
            # Create agent with appropriate settings
            agent_params = {
                "task": task,
                "llm": llm,
                "browser_session": browser_session,
            }
            
            # Disable vision for models that don't support it
            is_deepseek = "deepseek" in self.model.lower()
            if is_deepseek:
                agent_params["use_vision"] = False
                logger.info("Vision disabled for DeepSeek model")
            
            agent = Agent(**agent_params)
            logger.info(f"Agent created with task length: {len(task)} chars")
            
            # Run the agent
            logger.info("Running AI agent for content extraction...")
            result = await agent.run()
            
            # Parse agent result - the agent should return structured data
            logger.info("Extraction completed, parsing results...")
            
            # The agent.run() returns agent output - we need to extract the final result
            # For now, create a structured result from the agent's history
            extraction_result = self._parse_agent_result(result, question)
            
            logger.info(f"Successfully extracted data for: {question}")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}", exc_info=True)
            raise
        
        finally:
            # Clean up Steel session if used
            if steel_client and session:
                try:
                    steel_client.sessions.release(session.id)
                    logger.info("Steel session released")
                except Exception as e:
                    logger.warning(f"Failed to release Steel session: {e}")
    
    def _parse_agent_result(self, agent_result: Any, question: str) -> ExtractionResult:
        """
        Parse agent result into structured ExtractionResult.
        
        Args:
            agent_result: Result from agent.run()
            question: Original question
            
        Returns:
            ExtractionResult object
        """
        logger.info(f"Parsing agent result, type: {type(agent_result)}")
        
        # Default structure
        result_data = {
            "url": "https://www.reddit.com/answers/",
            "question": question,
            "sources": [],
            "sections": [],
            "relatedPosts": [],
            "relatedTopics": []
        }
        
        def _load_json_if_possible(text: str) -> Optional[Dict[str, Any]]:
            """Attempt to robustly extract the first JSON object from a noisy string.
            Strategy:
            1) Prefer fenced ```json code blocks
            2) Fallback to any fenced code block containing an object
            3) Scan for the first balanced {...} and try to json.loads it
            4) Detect attachment file paths like /tmp/.../*.json and read
            """
            if not text:
                return None
            # 1) ```json fenced block
            try:
                m = re.search(r"```\s*json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
                if m:
                    candidate = m.group(1)
                    return json.loads(candidate)
            except Exception:
                pass
            # 2) any fenced block with an object
            try:
                m = re.search(r"```[\w\-]*\s*(\{[\s\S]*?\})\s*```", text)
                if m:
                    candidate = m.group(1)
                    return json.loads(candidate)
            except Exception:
                pass
            # 3) balanced brace scan
            try:
                start_indices = [i for i, ch in enumerate(text) if ch == '{']
                for start in start_indices:
                    brace = 0
                    in_str = False
                    esc = False
                    end = None
                    for i in range(start, len(text)):
                        ch = text[i]
                        if in_str:
                            if esc:
                                esc = False
                            elif ch == '\\':
                                esc = True
                            elif ch == '"':
                                in_str = False
                        else:
                            if ch == '"':
                                in_str = True
                            elif ch == '{':
                                brace += 1
                            elif ch == '}':
                                brace -= 1
                                if brace == 0:
                                    end = i + 1
                                    break
                    if end:
                        candidate = text[start:end]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            continue
            except Exception:
                pass
            # 4) attachment json path
            try:
                m = re.search(r"Attachment\s*:\s*(/[^\s]+\.json)", text)
                if m:
                    path = m.group(1)
                    if os.path.exists(path):
                        with open(path, 'r', encoding='utf-8') as f:
                            return json.load(f)
            except Exception:
                pass
            return None
        
        # Try different methods to extract the result
        try:
            # Method 1: Check if result has final_result method
            if hasattr(agent_result, 'final_result'):
                final_result = agent_result.final_result()
                logger.info(f"Got final_result: {type(final_result)}")
                if isinstance(final_result, str):
                    parsed = _load_json_if_possible(final_result)
                    if parsed:
                        result_data = parsed
                elif isinstance(final_result, dict):
                    result_data = final_result
            
            # Method 2: Check if result has history with extracted data
            if (not result_data or result_data.get('sections') == []) and hasattr(agent_result, 'history'):
                # Look for the last done action in history
                for item in reversed(getattr(agent_result, 'history', []) or []):
                    text = None
                    if hasattr(item, 'result') and item.result:
                        text = str(item.result)
                    elif hasattr(item, 'content') and item.content:
                        text = str(item.content)
                    if text:
                        parsed = _load_json_if_possible(text)
                        if parsed and ('url' in parsed or 'question' in parsed or 'sections' in parsed):
                            result_data = parsed
                            break
            
            # Method 3: Try to parse from string representation
            if result_data == {
                "url": "https://www.reddit.com/answers/",
                "question": question,
                "sources": [],
                "sections": [],
                "relatedPosts": [],
                "relatedTopics": []
            } and isinstance(agent_result, str):
                parsed = _load_json_if_possible(agent_result)
                if parsed:
                    result_data = parsed
        except Exception as e:
            logger.warning(f"Failed to parse agent result as JSON: {e}")
        
        # Normalize data types for Pydantic validation
        result_data = self._normalize_result_data(result_data)
        
        logger.info(
            f"Parsed result - URL: {result_data.get('url')}, Sections: {len(result_data.get('sections', []))}, Posts: {len(result_data.get('relatedPosts', []))}"
        )
        
        return ExtractionResult(**result_data)
    
    def _normalize_result_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize result data types for Pydantic validation.
        
        Args:
            data: Raw result data
            
        Returns:
            Normalized data dictionary
        """
        # Handle relatedPosts type conversions
        if 'relatedPosts' in data and data['relatedPosts']:
            for post in data['relatedPosts']:
                # Convert rank to string
                if 'rank' in post and isinstance(post['rank'], int):
                    post['rank'] = str(post['rank'])
                
                # Handle None values - convert to appropriate defaults
                if post.get('url') is None:
                    post['url'] = ""
                if post.get('title') is None:
                    post['title'] = ""
                if post.get('subreddit') is None:
                    post['subreddit'] = ""
                if post.get('domain') is None:
                    post['domain'] = ""
                if post.get('upvotes') is None:
                    post['upvotes'] = 0
                if post.get('comments') is None:
                    post['comments'] = 0
                if post.get('score') is None:
                    post['score'] = 0
        
        return data
    
    async def extract_generic_content(
        self,
        url: str,
        extraction_instructions: str
    ) -> Dict[str, Any]:
        """
        Extract content from any website with custom instructions.
        
        Args:
            url: Target URL
            extraction_instructions: What to extract and how
            
        Returns:
            Dictionary with extracted content
        """
        steel_client = None
        session = None
        
        try:
            logger.info(f"Starting generic extraction from: {url}")
            
            # Create Steel session
            steel_client = self._create_steel_client()
            session = steel_client.sessions.create()
            
            # Connect browser-use to Steel
            domain = os.getenv("DOMAIN", "http://localhost:3000")
            cdp_url = replace_protocol_mapping(domain)
            
            # Create AI agent
            llm = self._create_llm()
            task = f"Go to {url} and {extraction_instructions}"
            
            agent = Agent(
                task=task,
                llm=llm,
                browser_session=BrowserSession(cdp_url=cdp_url)
            )
            
            # Run extraction
            result = await agent.run()
            
            # Return raw result
            return {"url": url, "result": str(result)}
            
        finally:
            if steel_client and session:
                try:
                    steel_client.sessions.release(session.id)
                except Exception as e:
                    logger.warning(f"Failed to release Steel session: {e}")

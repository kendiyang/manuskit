"""
Test script for extraction service.
"""
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.services.extraction_service import ExtractionService

async def test_extraction():
    """Test the extraction service"""
    print("=" * 60)
    print("Testing ExtractionService")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. Initializing ExtractionService...")
        service = ExtractionService()
        print("   ✅ Service initialized successfully")
        
        # Test extraction
        print("\n2. Testing Reddit Answers extraction...")
        question = "how many planets are in our solar system?"
        print(f"   Question: {question}")
        
        result = await service.extract_reddit_answers(question)
        
        print("\n3. Extraction Result:")
        print(f"   URL: {result.url}")
        print(f"   Question: {result.question}")
        print(f"   Sources: {len(result.sources)} subreddits")
        print(f"   Sections: {len(result.sections)} sections")
        print(f"   Related Posts: {len(result.relatedPosts)} posts")
        print(f"   Related Topics: {len(result.relatedTopics)} topics")
        
        if result.sections:
            print("\n   First section:")
            print(f"     Heading: {result.sections[0].heading}")
            print(f"     Content items: {len(result.sections[0].content)}")
        
        print("\n" + "=" * 60)
        print("✅ Test passed!")
        print("=" * 60)
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\n💡 Please check your .env file:")
        print("   - MODEL should be set (e.g., gpt-4o-mini)")
        print("   - OPENAI_API_KEY should be set")
        return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_extraction())
    sys.exit(0 if success else 1)

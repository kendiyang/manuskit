"""
Data models for the web content extraction platform.
Follows the structure defined in examples/README.md
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Input Models
class ExtractionRequest(BaseModel):
    """Input schema for extraction requests"""
    question: str = Field(..., description="Question to search for answers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "tips to improve water pressure"
            }
        }


# Output Models
class PostMetadata(BaseModel):
    """Related post metadata"""
    rank: str  # Accept string but coerce from int
    title: str
    subreddit: str
    url: str
    upvotes: int = 0  # Default to 0 if None
    comments: int = 0  # Default to 0 if None
    domain: str = ""  # Default to empty string if None
    promoted: bool = False
    score: int = 0  # Default to 0 if None
    
    class Config:
        # Allow coercion of types (int -> str for rank)
        coerce_numbers_to_str = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversions"""
        if isinstance(obj, dict):
            # Convert rank to string if it's an int
            if 'rank' in obj and isinstance(obj['rank'], int):
                obj['rank'] = str(obj['rank'])
            # Handle None values
            if obj.get('domain') is None:
                obj['domain'] = ""
            if obj.get('upvotes') is None:
                obj['upvotes'] = 0
            if obj.get('comments') is None:
                obj['comments'] = 0
            if obj.get('score') is None:
                obj['score'] = 0
        return super().model_validate(obj)


class ContentSection(BaseModel):
    """Organized content section with heading"""
    heading: str
    content: List[str]


class ExtractionResult(BaseModel):
    """Output schema for extraction results"""
    url: str = Field(..., description="Reddit Answers page URL")
    question: str = Field(..., description="The question that was asked")
    sources: List[str] = Field(default_factory=list, description="Source subreddit URLs")
    sections: List[ContentSection] = Field(default_factory=list, description="Organized answer sections")
    relatedPosts: List[PostMetadata] = Field(default_factory=list, description="Related Reddit posts")
    relatedTopics: List[str] = Field(default_factory=list, description="Suggested related questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.reddit.com/answers/91ede21d-7f09-437e-91a6-4d5ae1f6d936",
                "question": "how many planet are in our solar system?",
                "sources": [
                    "https://www.reddit.com/r/threebodyproblem",
                    "https://www.reddit.com/r/technology"
                ],
                "sections": [
                    {
                        "heading": "Current Consensus",
                        "content": ["8 Planets: The current official count..."]
                    }
                ],
                "relatedPosts": [],
                "relatedTopics": []
            }
        }


# Task Management Models
class TaskInfo(BaseModel):
    """Task information for tracking"""
    task_id: str
    status: TaskStatus
    question: str
    created_at: datetime
    updated_at: datetime
    result: Optional[ExtractionResult] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskCreateResponse(BaseModel):
    """Response after creating a task"""
    task_id: str
    status: TaskStatus
    message: str


class TaskStatusResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: TaskStatus
    progress: Optional[str] = None
    result: Optional[ExtractionResult] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

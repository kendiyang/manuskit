"""
Task manager for handling async extraction tasks.
Provides task queuing, status tracking, and result storage.
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor

from src.models import TaskInfo, TaskStatus, ExtractionResult
from src.services.extraction_service import ExtractionService

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages async extraction tasks with status tracking"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        """
        Initialize task manager
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent extraction tasks
        """
        self.tasks: Dict[str, TaskInfo] = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        
        # Service instances
        self.extraction_service = ExtractionService()
        
        logger.info(f"TaskManager initialized with max {max_concurrent_tasks} concurrent tasks")
    
    def create_task(self, question: str) -> str:
        """
        Create a new extraction task
        
        Args:
            question: Question to extract answers for
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        task_info = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING,
            question=question,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.tasks[task_id] = task_info
        logger.info(f"Created task {task_id} for question: {question}")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """
        Get task information
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskInfo or None if not found
        """
        return self.tasks.get(task_id)
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[ExtractionResult] = None,
        error: Optional[str] = None,
        progress: Optional[str] = None
    ):
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status
            result: Extraction result (if completed)
            error: Error message (if failed)
            progress: Progress message
        """
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return
        
        task = self.tasks[task_id]
        task.status = status
        task.updated_at = datetime.utcnow()
        
        if result:
            task.result = result
        if error:
            task.error = error
        if progress:
            task.metadata["progress"] = progress
        
        logger.info(f"Task {task_id} updated to status: {status}")
    
    async def execute_task(self, task_id: str):
        """
        Execute an extraction task
        
        Args:
            task_id: Task ID to execute
        """
        async with self.semaphore:  # Limit concurrent tasks
            task = self.get_task(task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return
            
            try:
                # Update status to running
                self.update_task_status(
                    task_id,
                    TaskStatus.RUNNING,
                    progress="Starting extraction..."
                )
                
                # Execute extraction
                logger.info(f"Executing task {task_id}")
                result = await self.extraction_service.extract_reddit_answers(task.question)
                
                # Update with result
                self.update_task_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    result=result
                )
                
                logger.info(f"Task {task_id} completed successfully")
                
            except Exception as e:
                error_msg = f"Extraction failed: {str(e)}"
                logger.error(f"Task {task_id} failed: {error_msg}", exc_info=True)
                
                self.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error=error_msg
                )
    
    def submit_task(self, task_id: str):
        """
        Submit task for async execution
        
        Args:
            task_id: Task ID to submit
        """
        # Create task in event loop
        asyncio.create_task(self.execute_task(task_id))
        logger.info(f"Task {task_id} submitted for execution")
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> list[TaskInfo]:
        """
        List tasks with optional filtering
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of tasks to return
            
        Returns:
            List of TaskInfo objects
        """
        tasks = list(self.tasks.values())
        
        # Filter by status if provided
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if cancelled, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.PENDING:
            self.update_task_status(task_id, TaskStatus.CANCELLED)
            logger.info(f"Task {task_id} cancelled")
            return True
        
        logger.warning(f"Cannot cancel task {task_id} with status {task.status}")
        return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get task statistics
        
        Returns:
            Dictionary with task counts by status
        """
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                stats["pending"] += 1
            elif task.status == TaskStatus.RUNNING:
                stats["running"] += 1
            elif task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
            elif task.status == TaskStatus.CANCELLED:
                stats["cancelled"] += 1
        
        return stats

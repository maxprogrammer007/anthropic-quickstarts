from pydantic import BaseModel

# Pydantic models for data validation and serialization

class CreateTaskRequest(BaseModel):
    """Model for the request to create a new agent task."""
    prompt: str

class TaskResponse(BaseModel):
    """Model for the response when a task is created."""
    task_id: str
    prompt: str

class Message(BaseModel):
    """Model for a single message in a task's history."""
    role: str
    content: str
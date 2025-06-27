import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

# Correctly import the AgentManager from our agent_manager.py file
from .agent_manager import AgentManager

# Pydantic models (no changes here)
class CreateTaskRequest(BaseModel):
    prompt: str

class TaskResponse(BaseModel):
    task_id: str
    prompt: str

router = APIRouter(prefix="/api/v1", tags=["Agent Tasks"])

# This dictionary will now hold AgentManager instances.
active_managers: dict[str, AgentManager] = {}

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_request: CreateTaskRequest):
    """
    This endpoint is now just a trigger. It creates an AgentManager
    instance but DOES NOT start the agent. The agent will start when the
    WebSocket connects, ensuring we don't run agents without a listener.
    """
    manager = AgentManager(prompt=task_request.prompt)
    active_managers[manager.task_id] = manager
    print(f"Task {manager.task_id} created. Awaiting WebSocket connection.")

    return TaskResponse(task_id=manager.task_id, prompt=task_request.prompt)

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    Handles the real-time communication for a task.
    When a client connects, it starts the agent loop in the background
    and streams updates from the agent's queue to the client.
    """
    await websocket.accept()

    if task_id not in active_managers:
        await websocket.close(code=4004, reason="Task not found")
        return

    manager = active_managers[task_id]
    queue = manager.update_queue

    # Start the agent loop in a background task
    agent_task = asyncio.create_task(manager.run_agent())

    try:
        # Forward messages from the agent's queue to the WebSocket client
        while True:
            # Wait for the next message from the agent
            message = await queue.get()
            
            # Send the message to the client
            await websocket.send_json(message)
            
            # If the agent is finished, we can stop listening
            if message.get("content") == "Agent process finished.":
                break

    except WebSocketDisconnect:
        print(f"WebSocket for task {task_id} disconnected by client.")
        agent_task.cancel()  # Stop the agent if the client disconnects
    except Exception as e:
        print(f"An error occurred in WebSocket for task {task_id}: {e}")
    finally:
        # Clean up the task
        print(f"Cleaning up resources for task {task_id}.")
        del active_managers[task_id]
        print(f"Task {task_id} finished and cleaned up.")
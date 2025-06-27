import asyncio
import os
from functools import partial
from typing import List, Dict, Any

# --- Imports from the original demo code ---
# We can do this because we mounted the directory in docker-compose.yml
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolResult, ToolVersion

# Pydantic models from our api.py for type hinting
from .api import Message


class AgentManager:
    """
    Manages a single, long-running agent task.
    """

    def __init__(self, prompt: str):
        self.prompt = prompt
        self.task_id = f"task_{id(self)}"
        self.update_queue = asyncio.Queue()
        self.messages: List[Dict[str, Any]] = [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

    def _tool_output_callback(self, tool_output: ToolResult, tool_id: str):
        """
        A synchronous callback to handle tool results.
        Puts the tool output onto the queue to be sent over the WebSocket.
        """
        # We wrap the tool output in a standard message format
        message = {"role": "tool", "content": tool_output.to_dict(), "tool_id": tool_id}
        self.update_queue.put_nowait(message)

    def _agent_output_callback(self, content_block: Dict[str, Any]):
        """
        A synchronous callback to handle agent outputs (text, tool_use, thinking).
        Puts the agent's output onto the queue.
        """
        message = {"role": "assistant", "content": content_block}
        self.update_queue.put_nowait(message)

    async def run_agent(self):
        """
        Starts the agent sampling loop as a background task.
        """
        try:
            # We add a final "sentinel" message to the queue to signal completion.
            await self.update_queue.put({"role": "system", "content": "Agent process started."})

            # The main call to the original agent loop
            final_messages = await sampling_loop(
                # --- Configuration (we can expose these in the API later) ---
                system_prompt_suffix="",
                model="claude-3-5-sonnet-20240620", # Make sure this model is current
                provider=APIProvider.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                tool_version="computer_use_20241022",
                max_tokens=4096,
                # -----------------------------------------------------------
                
                messages=self.messages,
                
                # --- Callbacks ---
                # We use partial to pass `self` to the callback methods.
                output_callback=self._agent_output_callback,
                tool_output_callback=self._tool_output_callback,
                # This callback is for logging HTTP requests, we can ignore it for now
                api_response_callback=lambda req, resp, err: None,
            )
            self.messages = final_messages

        except Exception as e:
            # If the agent errors, put the error message on the queue
            error_message = {"role": "system", "content": f"An error occurred: {str(e)}"}
            await self.update_queue.put(error_message)
        finally:
            # Signal that the agent process has finished
            await self.update_queue.put({"role": "system", "content": "Agent process finished."})
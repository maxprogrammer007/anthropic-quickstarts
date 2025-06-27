import asyncio
import os
from functools import partial
from typing import List, Dict, Any

# --- Imports from the original demo code ---
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolResult, ToolVersion

# --- CORRECTED IMPORT ---
# Import 'Message' from our new schemas file to break the circular dependency.
from .schemas import Message


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
        # --- CORRECTED SERIALIZATION ---
        # The ToolResult object does not have a .to_dict() method.
        # We manually create a dictionary from its known attributes.
        content = {
            "output": tool_output.output,
            "error": tool_output.error,
            "base64_image": tool_output.base64_image,
        }
        # We wrap the tool output in a standard message format
        message = {"role": "tool", "content": content, "tool_id": tool_id}
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
            # We add a "system" message to the queue to signal the start.
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
                output_callback=self._agent_output_callback,
                tool_output_callback=self._tool_output_callback,
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
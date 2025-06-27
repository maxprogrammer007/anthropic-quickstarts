from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api import router as api_router
from .schemas import TaskResponse, CreateTaskRequest, Message


app = FastAPI(
    title="Claude Computer Use Agent API",
    description="API for managing and interacting with a computer-use agent.",
    version="0.1.0",
)

# --- Updated CORS Configuration ---
# We are making the configuration more explicit to handle all request types.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
# ------------------------------------

@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "ok", "message": "Welcome to the Agent API!"}

app.include_router(api_router)


# This check is good practice for modular applications.
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI
import uvicorn

# --- Imports we will add later ---
from .api import router as api_router  # UNCOMMENT THIS
# from .database import create_db_and_tables
# ---------------------------------

# --- Function to create database tables on startup (we will uncomment this later) ---
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()
# -----------------------------------------------------------------------------------


app = FastAPI(
    title="Claude Computer Use Agent API",
    description="API for managing and interacting with a computer-use agent.",
    version="0.1.0",
)


@app.get("/", tags=["Health Check"])
async def health_check():
    """
    A simple endpoint to confirm that the API server is running.
    """
    return {"status": "ok", "message": "Welcome to the Agent API!"}


# --- We will include our main API router here in the next step ---
app.include_router(api_router) # UNCOMMENT THIS
# -----------------------------------------------------------------


if __name__ == "__main__":
    # This allows running the app directly for local development without Docker
    uvicorn.run(app, host="0.0.0.0", port=8000)
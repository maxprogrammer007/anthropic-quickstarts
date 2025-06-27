FROM python:3.11-slim

WORKDIR /app

# Install backend-specific requirements
# Note: The COPY source path should be relative to the build context (new_arch/)
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ /app/

# The command to run the FastAPI server
# This is corrected to run as a module 'backend.main' to fix import errors.
# We also add --reload for development.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
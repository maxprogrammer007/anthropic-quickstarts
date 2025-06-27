FROM python:3.11-slim

WORKDIR /app

# Install backend-specific requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ /app/

# The command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
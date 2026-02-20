# Dockerfile for deployment
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
COPY web_app/requirements_web.txt web_app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt -r web_app/requirements_web.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p web_app/static/css web_app/static/js

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "web_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

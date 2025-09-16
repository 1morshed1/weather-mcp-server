# Use official Python image as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory in the container
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server code
COPY mcp/ ./mcp/

# Set environment variables
ENV PYTHONPATH=/app

# Expose the FastMCP port
EXPOSE 8000

# Command to run the server
CMD ["python", "mcp/weather.py"]

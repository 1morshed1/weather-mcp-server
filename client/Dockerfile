# Use official Python image as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the client code
COPY client/ ./client/

# Set environment variables
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "client/client.py", "--server.address", "0.0.0.0"]

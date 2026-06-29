# We use a lightweight Python image
FROM python:3.11-slim

# Prevent Python from generating .pyc files and let it know we are in container mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# We copy all your project code to the container
COPY . .

# Expose the port used by FastAPI (Render typically uses 10000, but FastAPI expects 8000)
EXPOSE 8000

# Command to start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
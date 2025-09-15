# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Set the PYTHONPATH environment variable so Python can find your modules
ENV PYTHONPATH=/app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We use --no-cache-dir to keep the image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container at /app
# This includes the 'engine', 'core', and 'shared' directories
COPY . .

# Expose port 8000 to allow communication to the uvicorn server
EXPOSE 8000

# Define the command to run your app using uvicorn
# This will be executed when the container starts
CMD ["uvicorn", "engine.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.2

# Install netcat, which is used by the entrypoint script to check the DB connection
RUN apt-get update && apt-get install -y netcat-traditional

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only the dependency file from the engine directory
COPY engine/pyproject.toml engine/poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-interaction

# Copy source code into the container
# This step is mainly for the initial image build.
# The volumes in docker-compose will keep it in sync.
COPY engine ./engine
COPY shared ./shared
COPY core ./core

# Copy and set permissions for the entrypoint script
COPY engine/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["entrypoint.sh"]

ENV PYTHONPATH=/app

# The command that the entrypoint will execute after the DB is ready
# This now just runs the main python script directly.
CMD ["poetry", "run", "python", "engine/app/main.py"]
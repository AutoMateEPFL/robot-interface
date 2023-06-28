# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10

# Install poetry
RUN pip install poetry

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /app

# Copy project specification and lock files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


# Install nano text editor
RUN apt-get update && apt-get install -y \
    nano \
    && rm -rf /var/lib/apt/lists/*

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# Copy the entire project
COPY . .

# Expose the port the app runs in
EXPOSE 8000
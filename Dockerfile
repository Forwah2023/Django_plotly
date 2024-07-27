# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install PostgreSQL client and other dependencies
RUN apt-get update && apt-get -y install libpq-dev gcc

# Install dependencies

RUN pip install --no-cache-dir virtualenv
RUN virtualenv venv
RUN . venv/bin/activate

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000



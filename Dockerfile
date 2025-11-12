### Multi-stage Dockerfile
### Stage 1: build wheels for dependencies (helps with native extensions)
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /wheels

# Install build dependencies for many common packages. Add/remove as needed.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       g++ \
       libssl-dev \
       libffi-dev \
       libxml2-dev \
       libxslt1-dev \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt /wheels/requirements.txt
RUN pip wheel --wheel-dir /wheels -r /wheels/requirements.txt


### Stage 2: final image based on Azure Functions Python base
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# Set function app environment
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    FUNCTIONS_WORKER_RUNTIME=python

# Copy pre-built wheels and install them (no network needed)
COPY --from=builder /wheels /wheels
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r /requirements.txt || pip install --no-cache-dir -r /requirements.txt

# Copy function app code
COPY . /home/site/wwwroot

# The base image already supplies the proper entrypoint for Azure Functions
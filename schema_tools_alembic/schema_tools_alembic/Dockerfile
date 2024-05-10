FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
RUN python -m venv /workspace/venv
ENV PATH="/workspace/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

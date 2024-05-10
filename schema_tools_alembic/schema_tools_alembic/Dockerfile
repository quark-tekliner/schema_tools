FROM python:3.12-slim
WORKDIR /workspace
RUN python -m venv /workspace/venv
ENV PATH="/workspace/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

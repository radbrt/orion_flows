FROM python:3.9-bullseye

RUN apt-get update && apt-get install -y \
    git-lfs && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://huggingface.co/databricks/dolly-v2-3b /model

WORKDIR /model
RUN git lfs pull

# COPY dollymodel ./dollymodel
# COPY simpleload.py .
COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt


WORKDIR /


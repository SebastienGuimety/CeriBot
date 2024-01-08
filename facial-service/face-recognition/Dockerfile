FROM ubuntu:22.04
RUN apt-get update &&  \
    #apt-get install -y software-properties-common &&  \
    #add-apt-repository ppa:deadsnakes/ppa -y &&  \
    #apt-get update &&  \
    apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
RUN poetry install
CMD ["python3", "main.py"]
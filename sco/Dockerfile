FROM pytorch/pytorch:latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential \
        git \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /

RUN mkdir -p /app \
&& mkdir -p /app/sco/_static

WORKDIR /app
COPY . /app/sco

# RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

# install torch for GPU version
# RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html
# RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install -r sco/requirements.txt -f https://data.dgl.ai/wheels/repo.html

# CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "--limit-concurrency", "10", "fastapi_main:app"]
CMD ["python", "-m", "sco", "--host", "0.0.0.0", "--port", "5555"]

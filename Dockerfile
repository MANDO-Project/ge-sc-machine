FROM python:3.8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential \
        git \
        nano \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /

RUN mkdir -p /app \
&& mkdir -p /app/sco/_static

WORKDIR /app
COPY . /app


# install torch for GPU version
# RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html

RUN pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/lts/1.8/cpu -f https://data.dgl.ai/wheels/repo.html

# CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "sco.main:app"]
CMD ["python", "-m", "sco", "--host", "0.0.0.0", "--port", "5555"]

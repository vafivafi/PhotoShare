FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /src

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./src ./src

CMD ["gunicorn", "src.app.main:app",
    "--workers", "4",
    "--worker-class", "uvicorn.workers.UvicornWorker",
    "--bind", "0.0.0.0:8000"]

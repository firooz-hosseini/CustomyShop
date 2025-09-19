FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY . /app/

EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
FROM python:3.9-alpine

WORKDIR /app

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --disable-pip-version-check --upgrade pip

COPY requirements.txt     /app/

RUN pip install --no-cache-dir -r ./requirements.txt

COPY *.py                 /app/
COPY template.config.yaml /app/

ENTRYPOINT python main.py
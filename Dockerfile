FROM python:3.11-bookworm

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./task-tracker-app /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["bash", "/entrypoint.sh"]


